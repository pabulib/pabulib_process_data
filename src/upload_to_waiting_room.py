"""Upload local .pb files into the admin waiting room on the remote server.

This script is intentionally simple, similar to ``start_process.py`` and
``run_output_checks.py``:

- by default it uploads all ``.pb`` files from ``src/output``
- it sends them to ``/app/waiting_room/admin`` inside the web container (used by ``/admin/upload``)
- files stay in the waiting room until you click Upload in the admin panel

Configuration is read in this order:
1. repository ``.env``
2. ``src/ssh_client/.env``
3. SSH config host provided via ``SSH_CONFIG_HOST`` (or ``ssh_config_host`` below)
4. direct environment variables
"""

from __future__ import annotations

import glob
import os
import sys
import warnings
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
DEFAULT_OUTPUT_DIR = SRC_ROOT / "output"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

try:
    from cryptography.utils import CryptographyDeprecationWarning  # type: ignore

    warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
except Exception:
    pass

from ssh_client.ssh_client import (
    SSHClientError,
    connect_from_env,
    connect_from_ssh_config,
)


def _load_envs() -> None:
    """Load repo and ssh-client .env files if present."""
    repo_env = REPO_ROOT / ".env"
    cli_env = SRC_ROOT / "ssh_client" / ".env"

    def _fallback_parse(path: Path, override: bool) -> None:
        try:
            with path.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if override or key not in os.environ:
                        os.environ[key] = value
        except Exception:
            pass

    try:
        from dotenv import load_dotenv  # type: ignore

        if repo_env.exists():
            load_dotenv(repo_env, override=False)
        if cli_env.exists():
            load_dotenv(cli_env, override=True)
    except Exception:
        if repo_env.exists():
            _fallback_parse(repo_env, override=False)
        if cli_env.exists():
            _fallback_parse(cli_env, override=True)


def _collect_files(local_glob: str) -> list[Path]:
    files = [Path(p) for p in glob.glob(local_glob)]
    files = [p for p in files if p.is_file() and p.suffix == ".pb"]
    return sorted(files, key=lambda p: p.name.lower())


_load_envs()

# ---------------
# Local settings
# ---------------

# If set, use this SSH config host from ~/.ssh/config.
# Leave as None to rely on SSH_CONFIG_HOST / SSH_HOST / .env.
ssh_config_host: str | None = None

# Local source selection.
# Examples:
#   files_in_output_dir = "*"
#   files_in_output_dir = "Poland_Warszawa_*"
#   files_in_output_dir = "cleaned/*"
files_in_output_dir = os.environ.get("UPLOAD_WAITING_ROOM_GLOB", "*")

# Absolute glob may be used instead of src/output.
# Example:
#   files_in_absolute_dir = "/path/to/custom/*.pb"
files_in_absolute_dir: str | None = os.environ.get("UPLOAD_WAITING_ROOM_ABSOLUTE_GLOB")

# Upload behavior.
force_overwrite = os.environ.get("UPLOAD_WAITING_ROOM_FORCE", "").lower() in {
    "1",
    "true",
    "yes",
}


if files_in_absolute_dir:
    path_to_all_files = files_in_absolute_dir
else:
    path_to_all_files = str(DEFAULT_OUTPUT_DIR / f"{files_in_output_dir}.pb")


files = _collect_files(path_to_all_files)

if not files:
    raise SystemExit(f"No .pb files found for pattern: {path_to_all_files}")

container_name = os.environ.get("SSH_DOCKER_CONTAINER")
waiting_room_dir = os.environ.get(
    "SSH_CONTAINER_UPLOAD_TMP_DIR", "/app/waiting_room/admin"
)

if not container_name:
    raise SystemExit(
        "Missing SSH_DOCKER_CONTAINER. Set it in .env or environment before running."
    )

print("Preparing upload to admin waiting room...")
print(f"Local pattern: {path_to_all_files}")
print(f"Files found: {len(files)}")
print(f"Container: {container_name}")
print(f"Waiting room dir: {waiting_room_dir}")
print("")
for file_path in files:
    print(f"  - {file_path.name}")
print("")

client = (
    connect_from_ssh_config(ssh_config_host) if ssh_config_host else connect_from_env()
)

ok_count = 0

try:
    client.connect()

    for file_path in files:
        result = client.upload_file_to_admin_in_container(
            file_path,
            container=container_name,
            dest_dir=waiting_room_dir,
            force_overwrite=force_overwrite,
        )
        if result.get("ok"):
            size = int(result.get("size") or 0)
            print(
                f"✓ {file_path.name} ({size / (1024 * 1024):.2f} MB) -> {result.get('remote_path')}"
            )
            ok_count += 1
        else:
            print(f"✗ {file_path.name}: {result.get('error')}")

    print("")
    print(f"Completed: {ok_count}/{len(files)} successful")
    print("These files are now in the admin waiting room (/admin/upload).")

    if ok_count != len(files):
        raise SystemExit(1)
except SSHClientError as exc:
    raise SystemExit(str(exc))
finally:
    try:
        client.disconnect()
    except Exception:
        pass
    try:
        client.disconnect()
    except Exception:
        pass
