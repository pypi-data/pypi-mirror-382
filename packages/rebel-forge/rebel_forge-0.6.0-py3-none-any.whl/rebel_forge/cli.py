"""Command-line entry point for rebel-forge."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import textwrap
import time
import webbrowser
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlparse

from .onboarding import ensure_onboarding, is_portal_alive, resolve_login_url

_PACKAGE_ROOT = Path(__file__).resolve().parent
_IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
_DEFAULT_EXPORT_DIR = Path.home() / "rebel-forge"
_REMOTE_FLAG = "--remote"
_PORTAL_ENV = "REBEL_FORGE_PORTAL_DIR"
_STATE_DIR = Path.home() / ".rebel-forge"
_PORTAL_PID_FILE = _STATE_DIR / "portal-dev.pid"
_PORTAL_LOG_FILE = _STATE_DIR / "portal-dev.log"
_PORTAL_START_TIMEOUT = 60
_DEFAULT_PATH = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


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


def _activate_workspace(target: Path) -> None:
    if not target.exists():
        return
    try:
        os.chdir(target)
    except (NotADirectoryError, PermissionError):
        return


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

    _activate_workspace(_DEFAULT_EXPORT_DIR)
    login_base = resolve_login_url()
    _ensure_portal_ready(login_base, _DEFAULT_EXPORT_DIR)
    ensure_onboarding(workspace=_DEFAULT_EXPORT_DIR)

    if not argv:
        _handle_zero_arg(login_base)
        return

    argv = _maybe_enable_remote(argv)
    sys.argv = [sys.argv[0], *argv]

    from .rebel_forge import main as forge_main

    forge_main()


def _handle_zero_arg(login_base: str) -> None:
    base = login_base.rstrip("/")
    portal_ready = is_portal_alive(login_base)
    opened = False
    if portal_ready:
        opened = webbrowser.open(f"{base}/cli", new=2, autoraise=True)
        opened = webbrowser.open(f"{base}/workspace", new=2, autoraise=True) or opened
    else:
        opened = webbrowser.open(f"{base}/cli", new=2, autoraise=True)
    _print_zero_arg_hint(login_base, portal_ready, opened)


def _print_zero_arg_hint(login_base: str, portal_ready: bool, opened_browser: bool) -> None:
    base = login_base.rstrip("/")
    status = "Portal is live" if portal_ready else "Portal is launching"
    browser_note = "Browser tab opened" if opened_browser else "Open the portal in your browser"
    message = f"""{status} at {base}.

What you can do next:
  • Sign in through {base}/cli to unlock the CLI.
  • Visit {base}/workspace to explore Rebel Forge in the browser.
  • Launch training anytime with `rebel-forge --config path/to/run.conf`.

{browser_note} if it did not open automatically.
"""
    print(textwrap.dedent(message))


def _ensure_portal_ready(login_base: str, workspace: Path) -> None:
    _cleanup_stale_portal()
    if not _login_is_local(login_base):
        return
    if is_portal_alive(login_base):
        return
    pid = _read_portal_pid()
    if pid and _pid_alive(pid):
        return
    portal_dir = _discover_portal_dir(workspace)
    if portal_dir is None:
        _print_portal_hint(login_base)
        return
    process = _spawn_portal_process(portal_dir, _extract_port(login_base))
    if process is None:
        _print_portal_hint(login_base)
        return
    deadline = time.time() + _PORTAL_START_TIMEOUT
    while time.time() < deadline:
        if is_portal_alive(login_base):
            return
        if process.poll() is not None:
            print(f"Portal dev server exited early (status {process.returncode}). See {_PORTAL_LOG_FILE} for details.")
            return
        time.sleep(1.0)
    print(f"Portal dev server did not become ready within {_PORTAL_START_TIMEOUT} seconds. See {_PORTAL_LOG_FILE} for logs.")


def _login_is_local(login_base: str) -> bool:
    parsed = urlparse(login_base)
    host = (parsed.hostname or "").lower()
    if host in _LOCAL_HOSTS:
        return True
    return host.endswith(".local")


def _extract_port(login_base: str) -> int:
    parsed = urlparse(login_base)
    if parsed.port:
        return parsed.port
    if parsed.scheme == "https":
        return 443
    return 3000


def _discover_portal_dir(workspace: Path) -> Optional[Path]:
    visited: set[Path] = set()
    for candidate in _candidate_portal_dirs(workspace):
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if resolved in visited:
            continue
        visited.add(resolved)
        if _looks_like_portal(resolved):
            return resolved
    return None


def _candidate_portal_dirs(workspace: Path) -> Iterable[Path]:
    env_value = os.environ.get(_PORTAL_ENV)
    if env_value:
        yield Path(env_value)
    seeds = [
        workspace,
        workspace.parent,
        Path.cwd(),
        _PACKAGE_ROOT.parent,
        _PACKAGE_ROOT.parent.parent,
        _PACKAGE_ROOT.parent.parent.parent,
        Path.home() / "rebel-frontend",
    ]
    suffixes = ("", "rebel-frontend", "frontend", "portal")
    for seed in seeds:
        if not seed:
            continue
        for suffix in suffixes:
            candidate = seed if suffix == "" else seed / suffix
            yield candidate


def _looks_like_portal(path: Path) -> bool:
    if "node_modules" in path.parts:
        return False
    package_json = path / "package.json"
    if not package_json.is_file():
        return False
    try:
        data = json.loads(package_json.read_text())
    except Exception:
        return False
    scripts = data.get("scripts")
    if isinstance(scripts, dict):
        dev_cmd = scripts.get("dev")
        if isinstance(dev_cmd, str) and "next" in dev_cmd.lower():
            return True
    if (path / "next.config.ts").is_file() or (path / "next.config.mjs").is_file() or (path / "next.config.js").is_file():
        return True
    return False


def _spawn_portal_process(portal_dir: Path, port: int) -> Optional[subprocess.Popen]:
    env = _portal_env(port)
    npm_path = shutil.which("npm", path=env.get("PATH"))
    if not npm_path:
        print("Unable to locate `npm`. Install Node.js or expose it via PATH to auto-start the portal.")
        return None
    command = [npm_path, "run", "dev", "--", "--port", str(port), "--hostname", "0.0.0.0"]
    creationflags = 0
    preexec_fn = None
    if os.name == "posix":
        preexec_fn = os.setsid
    elif os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    log_handle = open(_PORTAL_LOG_FILE, "ab", buffering=0)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_handle.write(f"\n--- [{timestamp}] Starting rebel-forge portal in {portal_dir}\n".encode())
    process = subprocess.Popen(
        command,
        cwd=portal_dir,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        env=env,
        preexec_fn=preexec_fn,
        creationflags=creationflags,
        close_fds=True,
    )
    _PORTAL_PID_FILE.write_text(str(process.pid))
    log_handle.flush()
    log_handle.close()
    return process


def _portal_env(port: Optional[int] = None) -> dict[str, str]:
    env = os.environ.copy()
    current_path = env.get("PATH", "")
    env["PATH"] = _DEFAULT_PATH if not current_path else f"{_DEFAULT_PATH}:{current_path}"
    env.setdefault("BROWSER", "none")
    env.setdefault("NEXT_TELEMETRY_DISABLED", "1")
    if port is not None:
        env["PORT"] = str(port)
    else:
        env.setdefault("PORT", "3000")
    return env


def _read_portal_pid() -> Optional[int]:
    if not _PORTAL_PID_FILE.is_file():
        return None
    try:
        return int(_PORTAL_PID_FILE.read_text().strip())
    except Exception:
        return None


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _cleanup_stale_portal() -> None:
    pid = _read_portal_pid()
    if pid is None:
        return
    if _pid_alive(pid):
        return
    try:
        _PORTAL_PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def _print_portal_hint(login_base: str) -> None:
    base = login_base.rstrip("/")
    message = f"""Unable to auto-start the Rebel Forge portal.
Set `{_PORTAL_ENV}` to your Next.js frontend directory or run `npm run dev` manually, then visit {base}.
"""
    print(textwrap.dedent(message))
    _cleanup_stale_portal()


if __name__ == "__main__":
    main()
