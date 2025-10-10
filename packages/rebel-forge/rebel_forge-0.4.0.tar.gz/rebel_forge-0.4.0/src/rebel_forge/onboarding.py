"""Interactive onboarding banner for the rebel-forge CLI."""
from __future__ import annotations

import os
import textwrap
import time
import webbrowser
from pathlib import Path
from urllib import request

_ASCII_LOGO = r"""
██████╗ ███████╗██████╗ ███████╗██╗      ███████╗ ██████╗  ██████╗ ███████╗
██╔══██╗██╔════╝██╔══██╗██╔════╝██║      ██╔════╝██╔═══██╗██╔════╝ ██╔════╝
██████╔╝█████╗  ██║  ██║█████╗  ██║      █████╗  ██║   ██║██║  ███╗█████╗  
██╔══██╗██╔══╝  ██║  ██║██╔══╝  ██║      ██╔══╝  ██║   ██║██║   ██║██╔══╝  
██║  ██║███████╗██████╔╝███████╗███████╗ ███████╗╚██████╔╝╚██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚══════╝ ╚══════╝ ╚═════╝  ╚═════╝ ╚══════╝
"""

_MARKER_DIR = Path.home() / ".rebel-forge"
_MARKER_PATH = _MARKER_DIR / "onboarding.done"
_DEFAULT_LOGIN_URL = "http://localhost:3000/cli"
_SKIP_ENV = "REBEL_FORGE_SKIP_ONBOARDING"
_URL_ENV_KEYS = (
    "REBEL_FORGE_LOGIN_URL",
    "REBEL_FORGE_FRONTEND_URL",
    "NEXT_PUBLIC_SITE_URL",
)
_TRUE_VALUES = {"1", "true", "yes", "on"}
_CLEAR_CMDS = ("clear", "cls")


def ensure_onboarding(*, workspace: Path) -> None:
    """Show the welcome banner and guide the user through Clerk login."""

    if _should_skip():
        return
    if _MARKER_PATH.exists():
        return

    login_url = _resolve_login_url()

    while True:
        _render_banner(login_url, workspace)
        choice = input("Select an option [Log In/Skip/Quit]: ").strip().lower()

        if choice in {"", "1", "login", "log in", "l"}:
            _launch_login(login_url)
            _await_confirmation(login_url)
            _mark_complete(login_url)
            break
        if choice in {"skip", "s"}:
            if _confirm_skip():
                break
            continue
        if choice in {"quit", "q", "exit"}:
            raise SystemExit("Aborted by user before onboarding completed.")

        print("Unrecognized option. Type 'login', 'skip', or 'quit'.")


def _should_skip() -> bool:
    value = os.environ.get(_SKIP_ENV)
    return value is not None and value.strip().lower() in _TRUE_VALUES


def _resolve_login_url() -> str:
    for key in _URL_ENV_KEYS:
        raw = os.environ.get(key)
        if raw:
            return raw.rstrip("/")
    return _DEFAULT_LOGIN_URL


def _render_banner(login_url: str, workspace: Path) -> None:
    _clear_screen()
    print(_ASCII_LOGO)
    body = f"""Welcome to REBEL FORGE.

• Workspace: {workspace}
• Login portal: {login_url}

Launch the Rebel Forge dashboard running via `npm run dev` and sign up with Clerk.
After you authenticate in the browser, return here and continue.

Options:
  [Log In]    Open the browser and continue once signed in.
  [Skip]      Skip onboarding for this session only.
  [Quit]      Exit without running rebel-forge.
"""
    print(textwrap.dedent(body))


def _clear_screen() -> None:
    for cmd in _CLEAR_CMDS:
        if os.system(cmd + " > /dev/null 2>&1") == 0:
            return


def _launch_login(login_url: str) -> None:
    target = login_url.rstrip("/")
    print(f"Opening {target} in your browser...")
    webbrowser.open(target, new=2, autoraise=True)


def _await_confirmation(login_url: str) -> None:
    print()
    print("Waiting for the Clerk app to respond...")
    _wait_for_frontend(login_url, attempts=5, delay_seconds=1.5)
    input("Press Enter after you have completed sign up in the browser.")


def _wait_for_frontend(login_url: str, *, attempts: int, delay_seconds: float) -> None:
    for attempt in range(1, attempts + 1):
        if _frontend_alive(login_url):
            if attempt > 1:
                print("Frontend is responding. Continue in the browser to finish sign up.")
            return
        print(f"Attempt {attempt}/{attempts}: {login_url} is not reachable. If needed run `npm run dev`.")
        time.sleep(delay_seconds)


def _frontend_alive(login_url: str) -> bool:
    try:
        with request.urlopen(login_url, timeout=1.5) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def _mark_complete(login_url: str) -> None:
    _MARKER_DIR.mkdir(parents=True, exist_ok=True)
    _MARKER_PATH.write_text(f"onboarding-url={login_url}\n")
    print("Onboarding complete. Welcome to Rebel Forge!\n")


def _confirm_skip() -> bool:
    answer = input("Skip onboarding for this session? [y/N]: ").strip().lower()
    return answer.startswith("y")


__all__ = ["ensure_onboarding"]
