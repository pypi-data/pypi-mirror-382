"""Interactive onboarding banner for the rebel-forge CLI."""
from __future__ import annotations

import json
import os
import textwrap
import time
import uuid
import webbrowser
from pathlib import Path
from urllib import request

ASCII_LOGO = r"""
╔══════════════════════════════╗
║  Welcome to Rebel Forge CLI  ║
╚══════════════════════════════╝
"""

ANSI_RED = "[38;5;160m"
ANSI_RESET = "[0m"


def render_logo(*, force_color: bool = False) -> str:
    """Return the REBEL FORGE ASCII logo with optional ANSI color."""
    if force_color:
        return f"{ANSI_RED}{ASCII_LOGO}{ANSI_RESET}"
    if os.environ.get("NO_COLOR"):
        return ASCII_LOGO
    return f"{ANSI_RED}{ASCII_LOGO}{ANSI_RESET}"
_MARKER_DIR = Path.home() / ".rebel-forge"
_MARKER_PATH = _MARKER_DIR / "onboarding.done"
_HANDSHAKE_PREFIX = "cli-handshake-"
_DEFAULT_LOGIN_URL = "http://localhost:3000"
_SKIP_ENV = "REBEL_FORGE_SKIP_ONBOARDING"
_AUTO_UNLOCK_ENV = "REBEL_FORGE_AUTO_UNLOCK"
_AUTO_HANDSHAKE_USER_ENV = "REBEL_FORGE_HANDSHAKE_USER"
_TRUE_VALUES = {"1", "true", "yes", "on"}
_CLEAR_CMDS = ("clear", "cls")
_POLL_ATTEMPTS = 240
_POLL_DELAY_SECONDS = 1.0
_DEFAULT_HANDSHAKE_USER = "cli-user"


def ensure_onboarding(*, workspace: Path) -> None:
    """Show the welcome banner and guide the user through Clerk login."""

    if _should_skip() or _MARKER_PATH.exists():
        return

    login_base = resolve_login_url()
    token = uuid.uuid4().hex
    handshake_path = _MARKER_DIR / f"{_HANDSHAKE_PREFIX}{token}"
    portal_url = f"{login_base.rstrip('/')}/cli?token={token}"

    handshake_path.unlink(missing_ok=True)

    if _auto_unlock_enabled():
        _render_banner(portal_url, workspace)
        _launch_login(portal_url)
        _write_handshake(handshake_path, token)
        _mark_complete(login_base)
        handshake_path.unlink(missing_ok=True)
        return

    while True:
        _render_banner(portal_url, workspace)
        choice = input("Press Enter to open Clerk sign in, 's' to skip, or 'quit' to exit: ").strip().lower()
        if choice in {"", "login", "sign", "sign in", "signin", "log in", "1"}:
            _launch_login(portal_url)
            if _await_handshake(portal_url, handshake_path, token):
                _mark_complete(login_base)
                handshake_path.unlink(missing_ok=True)
                break
            print("Still waiting for confirmation from the browser. Select Log In again after finishing Clerk.")
            continue
        if choice in {"skip", "s"}:
            if _confirm_skip():
                handshake_path.unlink(missing_ok=True)
                return
            continue
        if choice in {"quit", "q", "exit"}:
            raise SystemExit("Aborted before completing Rebel Forge onboarding.")
        print("Unrecognized option. Press Enter to Log In, type 's' to skip, or 'quit' to exit.")


def _should_skip() -> bool:
    return _coerce_bool(os.environ.get(_SKIP_ENV))


def _auto_unlock_enabled() -> bool:
    return _coerce_bool(os.environ.get(_AUTO_UNLOCK_ENV))


def resolve_login_url() -> str:
    for key in ("REBEL_FORGE_LOGIN_URL", "REBEL_FORGE_FRONTEND_URL", "NEXT_PUBLIC_SITE_URL"):
        raw = os.environ.get(key)
        if raw:
            return raw.rstrip("/")
    return _DEFAULT_LOGIN_URL


def _render_banner(portal_url: str, workspace: Path) -> None:
    _clear_screen()
    _print_logo()
    print()
    print("Sign in with Clerk to unlock the Rebel Forge CLI.\n")
    _print_ascii_button(" SIGN IN WITH REBEL " )
    print("Press Enter to launch the portal, 's' to skip once, or 'quit' to exit.")
    print()


def _print_ascii_button(label: str) -> None:
    padding = 4
    width = len(label) + padding
    top = f"╭{'─' * width}╮"
    mid = f"│{label.center(width)}│"
    bottom = f"╰{'─' * width}╯"
    print(f"{ANSI_RED}{top}{ANSI_RESET}")
    print(f"{ANSI_RED}{mid}{ANSI_RESET}")
    print(f"{ANSI_RED}{bottom}{ANSI_RESET}")

def _clear_screen() -> None:
    if _coerce_bool(os.environ.get("REBEL_FORGE_DISABLE_CLEAR")):
        return
    for cmd in _CLEAR_CMDS:
        if os.system(cmd + " > /dev/null 2>&1") == 0:
            return


def _print_logo() -> None:
    print(render_logo())


def _launch_login(portal_url: str) -> None:
    print(f"Opening {portal_url} in your browser…")
    webbrowser.open(portal_url, new=2, autoraise=True)


def _await_handshake(portal_url: str, handshake_path: Path, token: str) -> bool:
    print("Waiting for the CLI unlock signal from the browser…")
    if _auto_unlock_enabled():
        _write_handshake(handshake_path, token)
        return True
    for attempt in range(1, _POLL_ATTEMPTS + 1):
        if handshake_path.exists():
            return True
        if attempt == 1 or attempt % 20 == 0:
            if not is_portal_alive(portal_url):
                print("The portal is not responding yet. Ensure `npm run dev` is active.")
            else:
                print("Portal responding. Complete Clerk sign-in and wait for the automatic unlock.")
        time.sleep(_POLL_DELAY_SECONDS)
    return False


def is_portal_alive(portal_url: str) -> bool:
    base = portal_url.split("?", 1)[0]
    try:
        with request.urlopen(base, timeout=1.5) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def _write_handshake(handshake_path: Path, token: str) -> None:
    handshake_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "token": token,
        "userId": os.environ.get(_AUTO_HANDSHAKE_USER_ENV, _DEFAULT_HANDSHAKE_USER),
        "unlockedAt": time.time(),
    }
    handshake_path.write_text(json.dumps(payload, indent=2))


def _mark_complete(login_base: str) -> None:
    _MARKER_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"login_url": login_base, "completed_at": time.time()}
    _MARKER_PATH.write_text(json.dumps(payload, indent=2))
    print("Onboarding complete. Welcome to Rebel Forge!\n")


def _confirm_skip() -> bool:
    answer = input("Skip onboarding for this session? [y/N]: ").strip().lower()
    return answer.startswith("y")


def _coerce_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in _TRUE_VALUES


__all__ = ["ensure_onboarding", "resolve_login_url", "is_portal_alive", "render_logo", "ASCII_LOGO", "ANSI_RED", "ANSI_RESET"]
