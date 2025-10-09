"""Command-line entry point for rebel-forge."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent
_IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")


def _export_source(destination: str, force: bool) -> Path:
    dest_path = Path(destination).expanduser().resolve()
    if dest_path.exists() and not force:
        raise SystemExit(
            f"Destination '{dest_path}' already exists. Pass --force to overwrite."
        )
    if dest_path.exists() and force:
        shutil.rmtree(dest_path)
    shutil.copytree(_PACKAGE_ROOT, dest_path, ignore=_IGNORE_PATTERNS)
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
    _export_source(args.dest, args.force)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "source":
        _handle_source(sys.argv[2:])
        return

    from .qlora import main as qlora_main

    qlora_main()


if __name__ == "__main__":
    main()
