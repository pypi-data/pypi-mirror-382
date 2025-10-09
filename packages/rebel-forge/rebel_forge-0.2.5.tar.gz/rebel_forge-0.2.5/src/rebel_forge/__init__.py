"""Top-level package for rebel-forge."""
from __future__ import annotations

__all__ = ["main", "__version__"]
__version__ = "0.2.5"


def main() -> None:
    """Entry point for `python -m rebel_forge` and console script."""
    from .qlora import main as _qlora_main

    _qlora_main()
