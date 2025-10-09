"""Command-line entry point for rebel-forge."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent
_IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
_DEFAULT_EXPORT_DIR = Path.home() / "rebel-forge"


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


def main() -> None:
    _ensure_default_export()
    if len(sys.argv) > 1 and sys.argv[1] == "source":
        _handle_source(sys.argv[2:])
        return

    from .qlora import main as qlora_main

    qlora_main()


if __name__ == "__main__":
    main()
