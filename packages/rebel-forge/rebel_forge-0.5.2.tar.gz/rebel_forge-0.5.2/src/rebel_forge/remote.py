"""Remote execution helpers for delegating compute to Nebius GPUs."""
from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

_RUN_FLAG = "FORGE_REMOTE_ACTIVE"
_RUN_ID_ENV = "FORGE_REMOTE_RUN_ID"
_PROJECT_ROOT_ENV = "FORGE_REMOTE_PROJECT_ROOT"
_DEFAULT_REMOTE_ROOT = "~/forge_runs"
_DEFAULT_VENV = "~/venvs/rebel-forge"

_DEFAULT_EXCLUDES: tuple[str, ...] = (
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    "*.egg-info",
    ".venv",
    "venv",
    "env",
    ".DS_Store",
)

_ROOT_MARKERS: tuple[str, ...] = (
    "pyproject.toml",
    "setup.cfg",
    "setup.py",
    "requirements.txt",
    "Pipfile",
    "poetry.lock",
    ".git",
    ".hg",
)


class RemoteError(RuntimeError):
    """Raised when Nebius orchestration fails."""


@dataclass
class RemoteConfig:
    """Connection parameters for Nebius remote execution."""

    host: str
    username: str
    port: int = 22
    identity_path: Path | None = None
    known_hosts_path: Path | None = None
    strict_host_key: bool = False
    remote_root: str = _DEFAULT_REMOTE_ROOT
    python: str = "python3"
    venv_path: str | None = _DEFAULT_VENV
    rsync_bin: str = "rsync"
    ssh_bin: str = "ssh"
    extra_excludes: tuple[str, ...] = ()
    passthrough_env: tuple[str, ...] = (
        "PYTHONPATH",
        "HF_HOME",
        "HF_DATASETS_CACHE",
        "HF_TOKEN",
        "HUGGING_FACE_HUB_TOKEN",
        "WANDB_API_KEY",
    )

    @classmethod
    def from_env(
        cls,
        *,
        host: str | None = None,
        username: str | None = None,
        port: int | None = None,
        identity_path: str | None = None,
        remote_root: str | None = None,
        python: str | None = None,
        venv_path: str | None = None,
        strict_host_key: bool | None = None,
    ) -> "RemoteConfig":
        env = os.environ
        host = host or env.get("FORGE_REMOTE_HOST") or env.get("NEBIUS_HOST")
        username = username or env.get("FORGE_REMOTE_USER") or env.get("NEBIUS_USERNAME")
        port_val = (
            port
            or _coerce_int(env.get("FORGE_REMOTE_PORT"))
            or _coerce_int(env.get("NEBIUS_PORT"))
            or 22
        )
        identity_candidate = identity_path or env.get("FORGE_REMOTE_KEY_PATH") or env.get("NEBIUS_KEY_PATH")
        identity_raw = env.get("FORGE_REMOTE_KEY") or env.get("NEBIUS_PRIVATE_KEY")
        venv_path = venv_path or env.get("FORGE_REMOTE_VENV") or env.get("NEBIUS_VENV_PATH") or _DEFAULT_VENV
        remote_root = remote_root or env.get("FORGE_REMOTE_ROOT") or env.get("NEBIUS_REMOTE_ROOT") or _DEFAULT_REMOTE_ROOT
        python = python or env.get("FORGE_REMOTE_PYTHON") or env.get("NEBIUS_PYTHON") or "python3"
        strict_host = strict_host_key if strict_host_key is not None else (
            _coerce_bool(env.get("FORGE_REMOTE_STRICT_HOST"))
            or _coerce_bool(env.get("NEBIUS_STRICT_HOST"))
            or False
        )

        if not host or not username:
            raise RemoteError("Missing Nebius host or username; set FORGE_REMOTE_HOST/USER or NEBIUS_HOST/USERNAME.")

        identity_path_obj = _resolve_identity_file(identity_candidate, identity_raw)
        fingerprint = env.get("FORGE_REMOTE_HOST_FINGERPRINT") or env.get("NEBIUS_HOST_FINGERPRINT")
        known_hosts_path = None
        if fingerprint:
            known_hosts_path = _ensure_known_host(host, port_val, fingerprint)
            strict_host = True

        return cls(
            host=host,
            username=username,
            port=port_val,
            identity_path=identity_path_obj,
            known_hosts_path=known_hosts_path,
            strict_host_key=strict_host,
            remote_root=remote_root,
            python=python,
            venv_path=venv_path,
        )

    def ssh_target(self) -> str:
        return f"{self.username}@{self.host}"

    def base_ssh_args(self) -> list[str]:
        args = [self.ssh_bin, "-p", str(self.port)]
        if self.identity_path:
            args.extend(["-i", str(self.identity_path)])
        if self.known_hosts_path:
            args.extend(["-o", f"UserKnownHostsFile={self.known_hosts_path}"])
        elif not self.strict_host_key:
            args.extend(["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null"])
        args.extend(["-o", "BatchMode=yes"])
        return args

    def ssh_command(self, remote_command: str) -> list[str]:
        return self.base_ssh_args() + [self.ssh_target(), remote_command]

    def rsync_ssh_transport(self) -> str:
        return " ".join(shlex.quote(arg) for arg in self.base_ssh_args())

    def format_remote_path(self, run_dir: str) -> str:
        root = self.remote_root.rstrip("/")
        run_dir = run_dir.lstrip("/")
        return f"{root}/{run_dir}" if run_dir else root

    def env_passthrough(self) -> dict[str, str]:
        values: dict[str, str] = {}
        for key in self.passthrough_env:
            value = os.environ.get(key)
            if value:
                values[key] = value
        return values


def ensure_remote(
    *,
    project_root: str | os.PathLike[str] | None = None,
    script_path: str | os.PathLike[str] | None = None,
    run_id: str | None = None,
    excludes: Iterable[str] | None = None,
    config: RemoteConfig | None = None,
    sync: bool = True,
    install_requires: bool = False,
) -> bool:
    """Ensure the active script executes on Nebius. Returns True when already remote."""

    if os.environ.get(_RUN_FLAG) == "1":
        return True

    cfg = config or RemoteConfig.from_env()
    _normalize_binaries(cfg)
    script = Path(script_path or sys.argv[0]).resolve()
    if not script.exists():
        raise RemoteError(f"Script not found: {script}")

    root = Path(project_root).resolve() if project_root else _discover_project_root(script)
    try:
        rel_script = script.relative_to(root)
    except ValueError as exc:  # pragma: no cover
        raise RemoteError(f"Script {script} is outside the project root {root}") from exc

    excludes_set = tuple(dict.fromkeys([*_DEFAULT_EXCLUDES, *(excludes or ()), *cfg.extra_excludes]))
    run_slug = run_id or _default_run_id(root)
    remote_project_dir = cfg.format_remote_path(run_slug)

    if sync:
        _sync_project(cfg, root, remote_project_dir, excludes_set)
    if install_requires:
        _install_remote_requirements(cfg, remote_project_dir)

    remote_project_shell = _remote_shell_path(remote_project_dir)
    remote_env: dict[str, str] = {
        _RUN_FLAG: "1",
        _RUN_ID_ENV: run_slug,
        _PROJECT_ROOT_ENV: remote_project_shell,
    }
    remote_env.update(cfg.env_passthrough())

    rel_parent = rel_script.parent
    remote_cwd_shell = remote_project_shell
    if rel_parent != Path("."):
        remote_cwd_shell = f"{remote_project_shell}/{rel_parent.as_posix()}"

    command = [cfg.python, rel_script.name, *sys.argv[1:]]
    exit_code = run_remote_command(cfg, command, remote_cwd=remote_cwd_shell, env=remote_env)
    raise SystemExit(exit_code)


def run_remote_command(
    config: RemoteConfig,
    command: Sequence[str] | str,
    *,
    remote_cwd: str | None = None,
    env: Mapping[str, str] | None = None,
    stream_output: bool = True,
) -> int:
    """Execute a command on Nebius and return its exit status."""

    _normalize_binaries(config)
    remote_segments: list[str] = []
    if config.venv_path:
        venv_shell = _remote_shell_path(config.venv_path)
        remote_segments.append(f'source "{venv_shell}/bin/activate"')
    if remote_cwd:
        shell_cwd = _remote_shell_path(remote_cwd)
        remote_segments.append(f'cd "{shell_cwd}"')

    assignments = []
    if env:
        for key, value in env.items():
            assignments.append(f"{key}={shlex.quote(value)}")
    cmd_str = command if isinstance(command, str) else _join_command(command)
    if assignments:
        cmd_str = f"{' '.join(assignments)} {cmd_str}".strip()
    remote_segments.append(cmd_str)

    remote_command = " && ".join(remote_segments)
    ssh_args = config.ssh_command(remote_command)
    return _run_subprocess(ssh_args, stream_output=stream_output, check=False)


def sync_project(
    *,
    config: RemoteConfig | None = None,
    source: str | os.PathLike[str] | None = None,
    run_id: str | None = None,
    excludes: Iterable[str] | None = None,
) -> str:
    """Synchronize a project tree to Nebius and return the remote path."""

    cfg = config or RemoteConfig.from_env()
    _normalize_binaries(cfg)
    root = Path(source or os.getcwd()).resolve()
    if not root.exists():
        raise RemoteError(f"Source directory does not exist: {root}")
    run_slug = run_id or _default_run_id(root)
    excludes_set = tuple(dict.fromkeys([*_DEFAULT_EXCLUDES, *(excludes or ()), *cfg.extra_excludes]))
    remote_project_dir = cfg.format_remote_path(run_slug)
    _sync_project(cfg, root, remote_project_dir, excludes_set)
    return remote_project_dir


def _sync_project(config: RemoteConfig, root: Path, remote_dir: str, excludes: Iterable[str]) -> None:
    rsync_bin = shutil.which(config.rsync_bin) or shutil.which('/usr/bin/rsync') or shutil.which('/bin/rsync')
    if rsync_bin is None:
        raise RemoteError("rsync is required for remote sync but was not found on PATH")
    remote_shell_dir = _remote_shell_path(remote_dir)
    prep_cmd = config.ssh_command(f'mkdir -p "{remote_shell_dir}"')
    _run_subprocess(prep_cmd)

    rsync_cmd = [rsync_bin, "-az", "--delete"]
    for pattern in excludes:
        rsync_cmd.extend(["--exclude", pattern])
    rsync_cmd.extend([
        "-e",
        config.rsync_ssh_transport(),
        f"{root}/",
        f"{config.ssh_target()}:{remote_shell_dir}/",
    ])
    _run_subprocess(rsync_cmd)


def _install_remote_requirements(config: RemoteConfig, remote_dir: str) -> None:
    requirements_path = _remote_shell_path(f"{remote_dir}/requirements.txt")
    python_prefix = ""
    if config.venv_path:
        venv_shell = _remote_shell_path(config.venv_path)
        python_prefix = f'source "{venv_shell}/bin/activate" && '
    remote = (
        f'if [ -f "{requirements_path}" ]; then '
        f"  {python_prefix}pip install -r \"{requirements_path}\"; "
        f"fi"
    )
    _run_subprocess(config.ssh_command(remote))


def _discover_project_root(path: Path) -> Path:
    current = path if path.is_dir() else path.parent
    for parent in [current, *current.parents]:
        for marker in _ROOT_MARKERS:
            if (parent / marker).exists():
                return parent
    return current


def _default_run_id(root: Path) -> str:
    slug = _slugify(root.name)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    short = uuid.uuid4().hex[:8]
    return f"{slug}-{timestamp}-{short}"


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "forge"


def _join_command(command: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def _coerce_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _coerce_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}



def _normalize_binaries(config: RemoteConfig) -> None:
    config.ssh_bin = _resolve_executable(config.ssh_bin, "ssh")
    config.rsync_bin = _resolve_executable(config.rsync_bin, "rsync")


def _resolve_executable(candidate: str | None, fallback: str) -> str:
    for name in (candidate, fallback, f"/usr/bin/{fallback}", f"/bin/{fallback}"):
        if not name:
            continue
        if name.startswith('/'):
            path = Path(name)
            if path.exists() and path.is_file():
                return str(path)
        else:
            resolved = shutil.which(name)
            if resolved:
                return resolved
    return candidate or fallback


def _resolve_identity_file(candidate: str | None, raw_key: str | None) -> Path | None:
    if candidate:
        candidate_path = Path(candidate).expanduser().resolve()
        if candidate_path.exists():
            _ensure_key_permissions(candidate_path)
            return candidate_path
    repo_key = Path(".nebius_key")
    if repo_key.exists():
        _ensure_key_permissions(repo_key)
        return repo_key.resolve()
    if raw_key and "BEGIN" in raw_key and len(raw_key.strip()) > 80:
        cache_dir = Path.home() / ".cache" / "rebel-forge"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_key = cache_dir / "nebius_key"
        if not cache_key.exists() or cache_key.read_text() != raw_key:
            cache_key.write_text(raw_key)
        _ensure_key_permissions(cache_key)
        return cache_key
    default = Path.home() / ".ssh" / "id_rsa"
    if default.exists():
        _ensure_key_permissions(default)
        return default
    return None


def _remote_shell_path(path: str | None) -> str:
    if not path:
        return ""
    if path.startswith("~/"):
        return f"$HOME/{path[2:]}"
    return path


def _ensure_key_permissions(path: Path) -> None:
    try:
        path.chmod(0o600)
    except PermissionError:
        pass


def _ensure_known_host(host: str, port: int, fingerprint: str) -> Path:
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    known_hosts = ssh_dir / "rebel-forge_known_hosts"
    fingerprint = fingerprint.strip()
    entry = f"[{host}]:{port} {fingerprint}\n"
    if known_hosts.exists():
        existing = known_hosts.read_text()
        if entry in existing:
            return known_hosts
    with known_hosts.open("a", encoding="utf-8") as handle:
        handle.write(entry)
    return known_hosts


def _run_subprocess(cmd: Sequence[str], *, stream_output: bool = True, check: bool = True) -> int:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE if stream_output else subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if stream_output and process.stdout is not None:
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
    code = process.wait()
    if check and code != 0:
        joined = " ".join(shlex.quote(part) for part in cmd)
        raise RemoteError(f"Command failed with exit code {code}: {joined}")
    return code


__all__ = [
    "RemoteConfig",
    "RemoteError",
    "ensure_remote",
    "run_remote_command",
    "sync_project",
]
