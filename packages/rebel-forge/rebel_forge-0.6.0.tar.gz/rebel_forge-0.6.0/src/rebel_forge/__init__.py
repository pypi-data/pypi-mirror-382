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

__version__ = "0.6.0"


def main() -> None:
    """Entry point for `python -m rebel_forge` and the console script."""
    from .rebel_forge import main as _forge_main

    _forge_main()
