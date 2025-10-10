"""Top-level package for rebel-forge."""
from __future__ import annotations

from .remote import RemoteConfig, RemoteError, ensure_remote, run_remote_command, sync_project
from . import sample as sample

__all__ = [
    "main",
    "__version__",
    "RemoteConfig",
    "RemoteError",
    "ensure_remote",
    "run_remote_command",
    "sync_project",
    "sample",
]

__version__ = "0.3.2"


def main() -> None:
    """Entry point for `python -m rebel_forge` and the console script."""
    from .qlora import main as _qlora_main

    _qlora_main()
