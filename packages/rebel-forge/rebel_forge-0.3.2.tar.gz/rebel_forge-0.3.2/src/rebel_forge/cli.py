"""Command-line entry point for rebel-forge."""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List

_PACKAGE_ROOT = Path(__file__).resolve().parent
_IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
_DEFAULT_EXPORT_DIR = Path.home() / "rebel-forge"
_REMOTE_FLAG = "--remote"


def _export_source(destination: str, *, force: bool = False, quiet: bool = False, skip_if_exists: bool = False) -> Path:
    dest_path = Path(destination).expanduser().resolve()
    if dest_path.exists():
        if skip_if_exists and not force:
            return dest_path
        if not force:
            raise SystemExit(
                f"Destination '{dest_path}' already exists. Pass --force to overwrite or use a different path."
            )
        shutil.rmtree(dest_path)
    shutil.copytree(_PACKAGE_ROOT, dest_path, ignore=_IGNORE_PATTERNS)
    if not quiet:
        print(f"Exported rebel-forge sources to {dest_path}")
    return dest_path


def _handle_source(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(
        prog="rebel-forge source",
        description="Export the installed rebel-forge sources to a directory",
    )
    parser.add_argument(
        "--dest",
        default="rebel-forge-src",
        help="Destination directory for the exported sources (default: rebel-forge-src)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the destination directory if it already exists.",
    )
    args = parser.parse_args(argv)
    _export_source(args.dest, force=args.force)


def _ensure_default_export() -> None:
    try:
        _export_source(str(_DEFAULT_EXPORT_DIR), skip_if_exists=True, quiet=True)
    except Exception:
        # Failing to export automatically should not block CLI usage.
        pass


def _consume_remote_flag(argv: List[str]) -> tuple[list[str], bool]:
    cleaned: list[str] = []
    remote_requested = False
    for arg in argv:
        if arg == _REMOTE_FLAG:
            remote_requested = True
            continue
        if arg.startswith(f"{_REMOTE_FLAG}="):
            _, value = arg.split("=", 1)
            remote_requested = _coerce_bool(value)
            continue
        cleaned.append(arg)
    return cleaned, remote_requested


def _coerce_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _maybe_enable_remote(argv: list[str]) -> list[str]:
    argv, flag_requested = _consume_remote_flag(argv)
    env_requested = _coerce_bool(os.environ.get("FORGE_REMOTE_AUTO"))
    if flag_requested or env_requested:
        from .remote import ensure_remote

        ensure_remote()
    return argv


def main() -> None:
    _ensure_default_export()
    argv = sys.argv[1:]
    if argv and argv[0] == "source":
        _handle_source(argv[1:])
        return

    argv = _maybe_enable_remote(argv)
    sys.argv = [sys.argv[0], *argv]

    from .qlora import main as qlora_main

    qlora_main()


if __name__ == "__main__":
    main()
