
#!/usr/bin/env python3
"""QLoRA fine-tuning utility with optional 4-bit quantization and config support."""

from __future__ import annotations

import argparse
import configparser
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Optional

os.environ.setdefault("BITSANDBYTES_NOWELCOME", "1")
os.environ.setdefault("BITSANDBYTES_CUDA_VERSION", "124")

try:
    import torch
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "PyTorch is required for rebel-forge. Install with `pip install rebel-forge[cpu]` or `pip install rebel-forge[cuda]` to include optional GPU extras, or supply your own torch build."
    ) from exc
from datasets import Dataset, load_dataset
from peft import LoraConfig, PeftModel, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
    set_seed,
)

try:
    from transformers import BitsAndBytesConfig  # type: ignore
    _BITSANDBYTES_AVAILABLE = True
except Exception:
    BitsAndBytesConfig = None  # type: ignore
    _BITSANDBYTES_AVAILABLE = False

SUPPORTED_QUANT_TYPES = {"nf4", "fp4"}
DEFAULT_TARGET_MODULES = "q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj"
TEXT_FIELD = "__text__"


def load_config(path: str) -> Dict[str, Any]:
    parser = configparser.ConfigParser()
    with open(path, "r", encoding="utf-8") as handle:
        parser.read_file(handle)

    cfg: Dict[str, Any] = {}

    if parser.has_section("model"):
        model_sec = parser["model"]
        cfg.update({
            "base_model": model_sec.get("base_model"),
            "output_dir": model_sec.get("output_dir"),
            "quant_type": model_sec.get("quant_type"),
            "no_quant": model_sec.getboolean("no_quant", fallback=False),
            "merge_full_model": model_sec.getboolean("merge_full_model", fallback=False),
        })

    if parser.has_section("data"):
        data_sec = parser["data"]
        cfg.update({
            "format": data_sec.get("format"),
            "text_column": data_sec.get("text_column"),
            "instruction_column": data_sec.get("instruction_column"),
            "input_column": data_sec.get("input_column"),
            "response_column": data_sec.get("response_column"),
            "system_column": data_sec.get("system_column"),
            "system_prompt": data_sec.get("system_prompt"),
            "train_data": data_sec.get("train_data"),
            "train_split": data_sec.get("train_split"),
            "eval_data": data_sec.get("eval_data"),
            "eval_split": data_sec.get("eval_split"),
            "test_data": data_sec.get("test_data"),
            "test_split": data_sec.get("test_split"),
        })

    if parser.has_section("training"):
        train_sec = parser["training"]
        cfg.update({
            "seed": train_sec.getint("seed", fallback=42),
            "batch_size": train_sec.getint("batch_size", fallback=1),
            "gradient_accumulation_steps": train_sec.getint("gradient_accumulation_steps", fallback=8),
            "epochs": train_sec.getint("epochs", fallback=3),
            "max_steps": train_sec.getint("max_steps", fallback=-1),
            "learning_rate": train_sec.getfloat("learning_rate", fallback=2e-4),
            "weight_decay": train_sec.getfloat("weight_decay", fallback=0.0),
            "warmup_ratio": train_sec.getfloat("warmup_ratio", fallback=0.03),
            "logging_steps": train_sec.getint("logging_steps", fallback=10),
            "save_steps": train_sec.getint("save_steps", fallback=200),
            "eval_steps": train_sec.getint("eval_steps", fallback=200),
            "no_eval": train_sec.getboolean("no_eval", fallback=False),
            "bf16": train_sec.getboolean("bf16", fallback=False),
            "max_length": train_sec.getint("max_length", fallback=1024),
        })

    if parser.has_section("lora"):
        lora_sec = parser["lora"]
        cfg.update({
            "lora_r": lora_sec.getint("lora_r", fallback=64),
            "lora_alpha": lora_sec.getfloat("lora_alpha", fallback=16.0),
            "lora_dropout": lora_sec.getfloat("lora_dropout", fallback=0.05),
            "target_modules": lora_sec.get("target_modules"),
        })

    return {k: v for k, v in cfg.items() if v is not None}


def parse_args() -> argparse.Namespace:
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("--config", required=True, help="Path to configuration .conf file")
    config_args, remaining = base_parser.parse_known_args()

    config_path = os.path.abspath(config_args.config)
    defaults = load_config(config_path)

    parser = argparse.ArgumentParser(description="Train a model with QLoRA adapters")
    parser.set_defaults(**defaults)
    parser.set_defaults(config=config_path)

    parser.add_argument("--config", help=argparse.SUPPRESS)
    parser.add_argument("--base-model")
    parser.add_argument("--train-data")
    parser.add_argument("--train-split", default="train")
    parser.add_argument("--eval-data")
    parser.add_argument("--eval-split", default="validation")
    parser.add_argument("--test-data")
    parser.add_argument("--test-split", default="test")

    parser.add_argument("--format", choices=["plain", "chat"], default="plain")
    parser.add_argument("--text-column", default="text")
    parser.add_argument("--instruction-column", default="instruction")
    parser.add_argument("--input-column")
    parser.add_argument("--response-column", default="response")
    parser.add_argument("--system-column")
    parser.add_argument("--system-prompt", default="")
    parser.add_argument("--max-length", type=int, default=1024)

    parser.add_argument("--output-dir")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--warmup-ratio", type=float, default=0.03)
    parser.add_argument("--logging-steps", type=int, default=10)
    parser.add_argument("--save-steps", type=int, default=200)
    parser.add_argument("--eval-steps", type=int, default=200)
    parser.add_argument("--no-eval", action="store_true")
    parser.add_argument("--bf16", action="store_true")

    parser.add_argument("--lora-r", type=int, default=64)
    parser.add_argument("--lora-alpha", type=float, default=16.0)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--target-modules", default=None)

    parser.add_argument("--quant-type", choices=sorted(SUPPORTED_QUANT_TYPES), default="nf4")
    parser.add_argument("--merge-full-model", action="store_true")
    parser.add_argument("--no-quant", action="store_true")

    args = parser.parse_args(remaining)
    if not args.target_modules:
        if defaults.get("target_modules"):
            args.target_modules = defaults["target_modules"]
        else:
            args.target_modules = DEFAULT_TARGET_MODULES
    args.config = config_path

    for field in ("base_model", "train_data", "output_dir"):
        if getattr(args, field) in (None, ""):
            parser.error(f"'{field}' must be provided in the config file or CLI.")

    return args


def available_compute_dtype(force_bf16: bool) -> torch.dtype:
    if not torch.cuda.is_available():
        return torch.float32
    if force_bf16 and torch.cuda.is_bf16_supported():
        return torch.bfloat16
    if torch.cuda.is_bf16_supported():
        return torch.bfloat16
    return torch.float16


def load_dataset_auto(path: Optional[str], split: str) -> Optional[Dataset]:
    if path is None:
        return None

    path = os.path.expanduser(path)
    if os.path.isdir(path):
        return load_dataset("json", data_dir=path, split=split)

    suffix = Path(path).suffix.lower()
    data_files = {split: path}
    if suffix in {".json", ".jsonl"}:
        return load_dataset("json", data_files=data_files, split=split)
    if suffix in {".csv", ".tsv"}:
        fmt = "csv"
        kwargs = {"delimiter": "	"} if suffix == ".tsv" else {}
        return load_dataset(fmt, data_files=data_files, split=split, **kwargs)

    if "::" in path:
        name, subset = path.split("::", 1)
        return load_dataset(name, subset, split=split)
    return load_dataset(path, split=split)


def build_plain_text(example: Dict[str, Any], text_column: str) -> str:
    if text_column not in example:
        raise KeyError(f"Column '{text_column}' not found in example: {list(example.keys())}")
    return str(example[text_column])


def build_chat_text(example: Dict[str, Any], args: argparse.Namespace) -> str:
    instruction = str(example.get(args.instruction_column, "")).strip()
    response = str(example.get(args.response_column, "")).strip()
    user_input = str(example.get(args.input_column, "")).strip() if args.input_column else ""
    system_prompt = str(example.get(args.system_column, "")).strip() if args.system_column else args.system_prompt

    pieces = []
    if system_prompt:
        pieces.append(f"<|system|>\n{system_prompt}\n")
    if instruction:
        pieces.append(f"<|user|>\n{instruction}\n")
    if user_input:
        pieces.append(f"<|context|>\n{user_input}\n")
    pieces.append(f"<|assistant|>\n{response}")
    return "".join(pieces)


def tokenize_dataset(dataset: Dataset, tokenizer: Any, max_length: int) -> Dataset:
    def _tokenise(batch: Dict[str, Any]) -> Dict[str, Any]:
        return tokenizer(
            batch[TEXT_FIELD],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )

    return dataset.map(_tokenise, batched=True, remove_columns=[TEXT_FIELD])


def dataset_length(dataset: Optional[Dataset]) -> Optional[int]:
    if dataset is None:
        return None
    try:
        return len(dataset)
    except TypeError:
        return None


def main() -> None:
    args = parse_args()
    set_seed(args.seed)

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    compute_dtype = available_compute_dtype(args.bf16)

    use_4bit = _BITSANDBYTES_AVAILABLE and not args.no_quant
    if not torch.cuda.is_available():
        if use_4bit:
            print("[warn] CUDA not available; falling back to full precision training.")
        use_4bit = False

    quant_config = None
    if use_4bit and BitsAndBytesConfig is not None:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type=args.quant_type,
            bnb_4bit_compute_dtype=compute_dtype,
        )
    elif not use_4bit:
        print("[info] Running without 4-bit quantisation (full-precision finetuning).")

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model_kwargs: Dict[str, Any] = {
        "device_map": "auto" if torch.cuda.is_available() else None,
        "trust_remote_code": True,
    }
    if quant_config is not None:
        model_kwargs["quantization_config"] = quant_config
    else:
        model_kwargs["torch_dtype"] = compute_dtype if torch.cuda.is_available() else torch.float32

    try:
        model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            **{k: v for k, v in model_kwargs.items() if v is not None},
        )
    except (RuntimeError, ModuleNotFoundError) as error:
        if quant_config is not None:
            print(f"[warn] Failed to load model in 4-bit mode: {error}. Falling back to full precision.")
            quant_config = None
            model_kwargs.pop("quantization_config", None)
            model_kwargs["torch_dtype"] = compute_dtype if torch.cuda.is_available() else torch.float32
            model = AutoModelForCausalLM.from_pretrained(
                args.base_model,
                **{k: v for k, v in model_kwargs.items() if v is not None},
            )
        else:
            raise

    model = prepare_model_for_kbit_training(model)

    target_modules = [module.strip() for module in args.target_modules.split(",") if module.strip()]
    lora_cfg = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=target_modules or None,
    )
    model = get_peft_model(model, lora_cfg)

    train_ds = load_dataset_auto(args.train_data, args.train_split)
    eval_ds = None if args.no_eval else load_dataset_auto(args.eval_data, args.eval_split)
    test_ds = None if args.no_eval else load_dataset_auto(args.test_data, args.test_split)

    if args.format == "plain":
        def build(example: Dict[str, Any]) -> Dict[str, Any]:
            return {TEXT_FIELD: build_plain_text(example, args.text_column)}
    else:
        if not args.response_column:
            raise ValueError("--response-column is required for chat format")

        def build(example: Dict[str, Any]) -> Dict[str, Any]:
            return {TEXT_FIELD: build_chat_text(example, args)}

    train_ds = train_ds.map(build, remove_columns=train_ds.column_names)
    if eval_ds is not None:
        eval_ds = eval_ds.map(build, remove_columns=eval_ds.column_names)
    if test_ds is not None:
        test_ds = test_ds.map(build, remove_columns=test_ds.column_names)

    train_tok = tokenize_dataset(train_ds, tokenizer, args.max_length)
    eval_tok = tokenize_dataset(eval_ds, tokenizer, args.max_length) if eval_ds is not None else None
    test_tok = tokenize_dataset(test_ds, tokenizer, args.max_length) if test_ds is not None else None

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    do_eval = not args.no_eval and eval_tok is not None
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        warmup_ratio=args.warmup_ratio,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=max(1, args.batch_size * 2),
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        evaluation_strategy="steps" if do_eval else "no",
        eval_steps=args.eval_steps if do_eval else None,
        save_total_limit=2,
        bf16=torch.cuda.is_available() and compute_dtype == torch.bfloat16,
        fp16=torch.cuda.is_available() and compute_dtype == torch.float16,
        gradient_checkpointing=True,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tok,
        eval_dataset=eval_tok if do_eval else None,
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()

    metrics: Dict[str, Any] = {}
    if do_eval:
        eval_metrics = trainer.evaluate()
        if "eval_loss" in eval_metrics:
            eval_metrics["eval_perplexity"] = math.exp(min(20, eval_metrics["eval_loss"]))
        metrics.update(eval_metrics)
    if not args.no_eval and test_tok is not None:
        test_metrics = trainer.evaluate(eval_dataset=test_tok)
        if "eval_loss" in test_metrics:
            test_metrics["eval_perplexity"] = math.exp(min(20, test_metrics["eval_loss"]))
        metrics.update({f"test_{k}": v for k, v in test_metrics.items()})

    trainer.save_model()
    tokenizer.save_pretrained(output_dir)

    merged_output: Optional[Path] = None
    if args.merge_full_model:
        base_fp_dtype = torch.bfloat16 if compute_dtype == torch.bfloat16 else torch.float16
        print("Merging adapters into base model ...")
        base_model = AutoModelForCausalLM.from_pretrained(
            args.base_model,
            torch_dtype=base_fp_dtype,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
        )
        merged = PeftModel.from_pretrained(base_model, str(output_dir))
        merged = merged.merge_and_unload()
        merged_output = output_dir / "merged_model"
        merged_output.mkdir(exist_ok=True)
        merged.save_pretrained(merged_output)
        tokenizer.save_pretrained(merged_output)
        print(f"Merged model saved to {merged_output}")

    summary = {
        "config": args.config,
        "base_model": args.base_model,
        "output_dir": str(output_dir),
        "merged_output": str(merged_output) if merged_output else None,
        "format": args.format,
        "train_data": args.train_data,
        "eval_data": args.eval_data,
        "test_data": args.test_data,
        "train_samples": dataset_length(train_tok),
        "eval_samples": dataset_length(eval_tok),
        "test_samples": dataset_length(test_tok),
        "lora": {
            "r": args.lora_r,
            "alpha": args.lora_alpha,
            "dropout": args.lora_dropout,
            "target_modules": args.target_modules,
        },
        "hyperparameters": {
            "learning_rate": args.learning_rate,
            "epochs": args.epochs,
            "max_steps": args.max_steps,
            "batch_size": args.batch_size,
            "gradient_accumulation": args.gradient_accumulation_steps,
            "max_length": args.max_length,
        },
        "metrics": metrics,
    }

    with open(output_dir / "run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("Training complete. Summary written to run_summary.json")


if __name__ == "__main__":
    main()
