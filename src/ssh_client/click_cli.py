#!/usr/bin/env python3
"""
Click-based CLI for the standalone SSH client.

Provides convenient commands to:
- list: list remote .pb files
- upload: upload a file/dir/pattern of .pb files
- upload-all: upload all .pb files from the local src/output directory

Configuration priority (same as the ad-hoc CLI):
1) src/ssh_client/.env (overrides)
2) repository .env
3) SSH config (~/.ssh/config) if using --host or SSH_CONFIG_HOST
4) Direct environment variables

Usage examples:
  python src/ssh_client/click_cli.py list
  python src/ssh_client/click_cli.py list --dir pb_files
  python src/ssh_client/click_cli.py upload path/to/file.pb
  python src/ssh_client/click_cli.py upload path/to/dir --force
  python src/ssh_client/click_cli.py upload-all
  python src/ssh_client/click_cli.py --host szufa list
  python src/ssh_client/click_cli.py --host szufa upload-all --container pabulib-web-1
"""

from __future__ import annotations

import os
import shlex
import sys
import warnings
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Optional

import click

# Resolve repository and src roots to make imports and default paths robust
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
DEFAULT_OUTPUT_DIR = SRC_ROOT / "output"
DEFAULT_DOWNLOAD_DIR = Path(__file__).resolve().parent / "downloads"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _load_envs() -> None:
    """Load .env files (repo .env, then src/ssh_client/.env overriding)."""
    repo_env = REPO_ROOT / ".env"
    cli_env = Path(__file__).resolve().parent / ".env"

    def _fallback_parse(path: Path, override: bool = False):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if override or k not in os.environ:
                            os.environ[k] = v
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


_load_envs()

# Suppress noisy crypto deprecation warnings from paramiko/cryptography at import time
try:
    from cryptography.utils import CryptographyDeprecationWarning  # type: ignore

    warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)
except Exception:
    pass
try:
    from ssh_client.ssh_client import (
        SSHClientError,
        connect_from_env,
        connect_from_ssh_config,
    )
except Exception as e:
    click.echo(f"Error importing SSH client: {e}")
    sys.exit(1)


def _get_client(host: Optional[str]):
    return connect_from_ssh_config(host) if host else connect_from_env()


def _ensure_container(container: Optional[str]) -> Optional[str]:
    return container or os.environ.get("SSH_DOCKER_CONTAINER")


def _parse_multi(text: str) -> list[str]:
    """Parse comma and/or shell-style space separated inputs into a list.

    Examples:
      - "a b c" -> ["a", "b", "c"]
      - "a, b, c" -> ["a", "b", "c"]
      - "'a b',c" -> ["a b", "c"]
    """
    if not text:
        return []
    # First split shell-style to respect quoted paths with spaces
    parts = shlex.split(text)
    # Then split any leftover commas inside parts
    out: list[str] = []
    for p in parts:
        if "," in p:
            out.extend([s for s in (x.strip() for x in p.split(",")) if s])
        else:
            out.append(p)
    # Remove empties and dedupe preserving order
    seen = set()
    deduped = []
    for item in out:
        if item and item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


@contextmanager
def _silence_io():
    """Silence stdout/stderr for a block (used to hide connection logs)."""
    with open(os.devnull, "w") as devnull, redirect_stdout(devnull), redirect_stderr(
        devnull
    ):
        yield


@contextmanager
def _silent_ssh_client(host: Optional[str]):
    """Yield a connected SSH client with prints suppressed, and auto-disconnect."""
    client = None
    try:
        with _silence_io():
            client = _get_client(host)
            client.connect()
        yield client
    finally:
        if client is not None:
            with _silence_io():
                try:
                    client.disconnect()
                except Exception:
                    pass


def _preview_and_confirm(files: list[Path]) -> bool:
    """Print a simple preview of files and ask for confirmation.

    Returns True if the user confirms the action, False otherwise.
    """
    if not files:
        click.echo("No files to process.")
        return False
    click.echo("The following files will be uploaded:")
    for f in files:
        click.echo(f"  - {f.name}")
    click.echo("")
    return click.confirm("Do you want to upload all of them?", default=False)


def _preview_and_confirm_download(files: list[Path], dest: Path) -> bool:
    """Preview files to download and ask for confirmation."""
    if not files:
        click.echo("No files to download.")
        return False
    click.echo(f"The following files will be downloaded to: {dest}")
    for f in files:
        click.echo(f"  - {f.name}")
    click.echo("")
    return click.confirm("Do you want to download all of them?", default=False)


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option(
    "--host",
    type=str,
    default=lambda: os.environ.get("SSH_CONFIG_HOST", ""),
    show_default=lambda: bool(os.environ.get("SSH_CONFIG_HOST")),
    help="SSH config host to use from ~/.ssh/config (or via SSH_CONFIG_HOST)",
)
@click.pass_context
def cli(ctx: click.Context, host: str):
    """SSH helper for working with remote PB files and Admin uploads."""
    ctx.ensure_object(dict)
    ctx.obj["host"] = host or None

    # Interactive menu when no subcommand is provided
    if ctx.invoked_subcommand is None:
        _interactive_menu(ctx)


@cli.command("list")
@click.option(
    "--dir",
    "directory",
    type=click.Choice(
        ["all", "pb_files", "pb_files_depreciated"], case_sensitive=False
    ),
    default="all",
    show_default=True,
    help="Which remote directory to list",
)
@click.pass_context
def list_cmd(ctx: click.Context, directory: str):
    """List remote .pb files."""
    host = ctx.obj.get("host")
    try:
        from ssh_client.ssh_client import SSHClientError  # local name for except

        with _silent_ssh_client(host) as client:
            if directory == "pb_files":
                files = client.list_pb_files()
                _print_file_list(files, title="PB Files")
            elif directory == "pb_files_depreciated":
                files = client.list_pb_depreciated_files()
                _print_file_list(files, title="PB Files (Depreciated)")
            else:
                data = client.list_all_pb_files()
                _print_file_list(data["pb_files"], title="PB Files")
                _print_file_list(
                    data["pb_files_depreciated"], title="PB Files (Depreciated)"
                )
    except SSHClientError as e:
        _err(str(e))
        raise SystemExit(1)
    except Exception as e:
        _err(f"Unexpected error: {e}")
        raise SystemExit(1)


@cli.command("upload")
@click.argument("path", required=False)
@click.option("--force", is_flag=True, help="Overwrite existing files in destination")
@click.option(
    "--container",
    type=str,
    default=None,
    help="Docker container name for Admin uploads",
)
@click.pass_context
def upload_cmd(
    ctx: click.Context, path: Optional[str], force: bool, container: Optional[str]
):
    """Upload .pb file(s).

    PATH can be a file, a directory (all .pb inside), or a glob pattern. If PATH is not
    provided, defaults to uploading all .pb files from src/output.
    """
    host = ctx.obj.get("host")
    target = Path(path) if path else DEFAULT_OUTPUT_DIR

    if not path:
        click.echo(f"No PATH provided; defaulting to local directory: {target}")

    container_name = _ensure_container(container)
    if not container_name:
        _err("Missing container name. Set SSH_DOCKER_CONTAINER or pass --container.")
        raise SystemExit(1)

    try:
        if target.is_file():
            with _silent_ssh_client(host) as client:
                _upload_one(client, target, container_name, force)
        elif target.is_dir():
            files = sorted(target.glob("*.pb"))
            if not files:
                _err(f"No .pb files found in {target}")
                raise SystemExit(1)
            if not _preview_and_confirm(files):
                click.echo("Aborted.")
                return
            with _silent_ssh_client(host) as client:
                _upload_many(client, files, container_name, force)
        else:
            # Try glob pattern (relative to current working directory)
            import glob

            matches = [Path(p) for p in glob.glob(str(target))]
            # Keep only .pb files
            matches = [m for m in matches if m.is_file() and m.suffix == ".pb"]
            if not matches:
                _err(f"No files matched: {target}")
                raise SystemExit(1)
            if not _preview_and_confirm(matches):
                click.echo("Aborted.")
                return
            with _silent_ssh_client(host) as client:
                _upload_many(client, matches, container_name, force)
    except SSHClientError as e:
        _err(str(e))
        raise SystemExit(1)
    except Exception as e:
        _err(f"Unexpected error: {e}")
        raise SystemExit(1)


@cli.command("download-all")
@click.option(
    "--dir",
    "directory",
    type=click.Choice(
        ["all", "pb_files", "pb_files_depreciated"], case_sensitive=False
    ),
    default="all",
    show_default=True,
    help="Which remote directory to download from",
)
@click.option(
    "--dest",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=DEFAULT_DOWNLOAD_DIR,
    show_default=True,
    help="Local destination directory",
)
@click.option("--force", is_flag=True, help="Overwrite existing local files")
@click.option(
    "--recursive/--no-recursive",
    default=True,
    show_default=True,
    help="Recurse into subdirectories on the server",
)
@click.pass_context
def download_all_cmd(
    ctx: click.Context, directory: str, dest: Path, force: bool, recursive: bool
):
    """Download .pb files from the server to a local directory."""
    host = ctx.obj.get("host")
    dest.mkdir(parents=True, exist_ok=True)

    try:
        with _silent_ssh_client(host) as client:
            from ssh_client.ssh_client import SSHClientError  # noqa

            groups: list[tuple[str, list[dict], str]]  # (group_name, files, base_dir)
            if directory == "pb_files":
                base = client.remote_pb_files_dir  # type: ignore[attr-defined]
                files = (
                    client.list_pb_files_recursive()
                    if recursive
                    else client.list_pb_files()
                )
                groups = [("pb_files", files, str(base))]
            elif directory == "pb_files_depreciated":
                base = client.remote_pb_depreciated_dir  # type: ignore[attr-defined]
                files = (
                    client.list_pb_depreciated_files_recursive()
                    if recursive
                    else client.list_pb_depreciated_files()
                )
                groups = [("pb_files_depreciated", files, str(base))]
            else:
                # both
                base_pb = client.remote_pb_files_dir  # type: ignore[attr-defined]
                base_dep = client.remote_pb_depreciated_dir  # type: ignore[attr-defined]
                files_pb = (
                    client.list_pb_files_recursive()
                    if recursive
                    else client.list_pb_files()
                )
                files_dep = (
                    client.list_pb_depreciated_files_recursive()
                    if recursive
                    else client.list_pb_depreciated_files()
                )
                groups = [
                    ("pb_files", files_pb, str(base_pb)),
                    ("pb_files_depreciated", files_dep, str(base_dep)),
                ]

            # Build download plan
            plan: list[tuple[str, Path]] = []  # list of (remote_path, local_path)
            preview: list[Path] = []
            for group_name, files, base_dir in groups:
                sub_dest = dest if directory != "all" else dest / group_name
                sub_dest.mkdir(parents=True, exist_ok=True)
                for info in files:
                    remote_path = info.get("path") or ""
                    name = info.get("name") or ""
                    if not remote_path or not name:
                        continue
                    # Preserve directory structure when recursive
                    relpath = name
                    if recursive and base_dir:
                        try:
                            prefix = base_dir.rstrip("/") + "/"
                            if remote_path.startswith(prefix):
                                relpath = remote_path[len(prefix) :]
                            else:
                                relpath = name
                        except Exception:
                            relpath = name

                    local_path = sub_dest / str(relpath)
                    plan.append((str(remote_path), local_path))
                    preview.append(local_path)

            if not plan:
                _err("No files found to download")
                raise SystemExit(1)

            if not _preview_and_confirm_download(preview, dest):
                click.echo("Aborted.")
                return

            # Execute downloads
            ok = 0
            for remote_path, local_path in plan:
                res = client.download_file(remote_path, local_path, overwrite=force)
                if res.get("ok"):
                    size = res.get("size") or 0
                    click.echo(
                        f"  ↓ {local_path.name} ({(int(size) /(1024*1024)):.2f} MB)"
                    )
                    ok += 1
                else:
                    click.echo(f"  ✗ {local_path.name}: {res.get('error')}")

            click.echo(f"Completed: {ok}/{len(plan)} successful")
            if ok != len(plan):
                raise SystemExit(1)
    except SSHClientError as e:
        _err(str(e))
        raise SystemExit(1)
    except Exception as e:
        _err(f"Unexpected error: {e}")
        raise SystemExit(1)


@cli.command("upload-all")
@click.option("--force", is_flag=True, help="Overwrite existing files in destination")
@click.option(
    "--container",
    type=str,
    default=None,
    help="Docker container name for Admin uploads",
)
@click.pass_context
def upload_all_cmd(ctx: click.Context, force: bool, container: Optional[str]):
    """Upload all .pb files from the local src/output directory."""
    host = ctx.obj.get("host")
    container_name = _ensure_container(container)
    if not container_name:
        _err("Missing container name. Set SSH_DOCKER_CONTAINER or pass --container.")
        raise SystemExit(1)

    files = sorted(DEFAULT_OUTPUT_DIR.glob("*.pb"))
    if not files:
        _err(f"No .pb files found in {DEFAULT_OUTPUT_DIR}")
        raise SystemExit(1)

    if not _preview_and_confirm(files):
        click.echo("Aborted.")
        return

    try:
        with _silent_ssh_client(host) as client:
            _upload_many(client, files, container_name, force)
    except SSHClientError as e:
        _err(str(e))
        raise SystemExit(1)
    except Exception as e:
        _err(f"Unexpected error: {e}")
        raise SystemExit(1)


@cli.command("upload-paths")
@click.argument("paths", nargs=-1, required=True)
@click.option("--force", is_flag=True, help="Overwrite existing files in destination")
@click.option(
    "--container",
    type=str,
    default=None,
    help="Docker container name for Admin uploads",
)
@click.pass_context
def upload_paths_cmd(
    ctx: click.Context, paths: tuple[str, ...], force: bool, container: Optional[str]
):
    """Upload .pb files from one or more paths or glob patterns (no directories)."""
    host = ctx.obj.get("host")
    container_name = _ensure_container(container)
    if not container_name:
        _err("Missing container name. Set SSH_DOCKER_CONTAINER or pass --container.")
        raise SystemExit(1)

    files: list[Path] = []
    for p in paths:
        pth = Path(p)
        if pth.is_file():
            if pth.suffix == ".pb":
                files.append(pth)
            else:
                click.echo(f"Skipping non-.pb file: {pth}")
        elif pth.is_dir():
            _err(f"'{pth}' is a directory. Use 'upload-dirs' for directories.")
            raise SystemExit(1)
        else:
            # Treat as glob pattern
            import glob

            for g in glob.glob(p):
                gp = Path(g)
                if gp.is_file() and gp.suffix == ".pb":
                    files.append(gp)

    # Deduplicate while preserving order
    files = list(dict.fromkeys(files))
    if not files:
        _err("No .pb files found to upload")
        raise SystemExit(1)

    # Preview list
    if not _preview_and_confirm(files):
        click.echo("Aborted.")
        return

    try:
        with _silent_ssh_client(host) as client:
            _upload_many(client, files, container_name, force)
    except SSHClientError as e:
        _err(str(e))
        raise SystemExit(1)
    except Exception as e:
        _err(f"Unexpected error: {e}")
        raise SystemExit(1)


@cli.command("upload-dirs")
@click.argument("dirs", nargs=-1, required=True)
@click.option("--force", is_flag=True, help="Overwrite existing files in destination")
@click.option(
    "--container",
    type=str,
    default=None,
    help="Docker container name for Admin uploads",
)
@click.pass_context
def upload_dirs_cmd(
    ctx: click.Context, dirs: tuple[str, ...], force: bool, container: Optional[str]
):
    """Upload all .pb files from one or more directories."""
    host = ctx.obj.get("host")
    container_name = _ensure_container(container)
    if not container_name:
        _err("Missing container name. Set SSH_DOCKER_CONTAINER or pass --container.")
        raise SystemExit(1)

    files: list[Path] = []
    for d in dirs:
        dp = Path(d)
        if not dp.is_dir():
            _err(f"Not a directory: {dp}")
            raise SystemExit(1)
        files.extend(sorted(dp.glob("*.pb")))

    # Deduplicate while preserving order
    files = list(dict.fromkeys(files))
    if not files:
        _err("No .pb files found in the provided directories")
        raise SystemExit(1)

    # Preview list
    if not _preview_and_confirm(files):
        click.echo("Aborted.")
        return

    try:
        with _silent_ssh_client(host) as client:
            _upload_many(client, files, container_name, force)
    except SSHClientError as e:
        _err(str(e))
        raise SystemExit(1)
    except Exception as e:
        _err(f"Unexpected error: {e}")
        raise SystemExit(1)


# -----------------
# Helper utilities
# -----------------


def _print_file_list(files, title: str) -> None:
    if not files:
        click.echo(f"\n{title}: No files found")
        return
    click.echo(f"\n{title}: {len(files)} files")
    click.echo("-" * 80)
    click.echo(f"{'Filename':<50} {'Size':>10} {'Modified':>20}")
    click.echo("-" * 80)
    total = 0
    for info in files:
        size_mb = info.get("size", 0) / (1024 * 1024)
        modified = info.get("modified")
        modified_str = modified.strftime("%Y-%m-%d %H:%M:%S") if modified else "-"
        click.echo(f"{info['name']:<50} {size_mb:>8.2f} MB  {modified_str}")
        total += info.get("size", 0)
    click.echo("-" * 80)
    click.echo(f"Total: {len(files)} files, {total / (1024 * 1024):.2f} MB")


def _upload_one(client, path: Path, container: str, force: bool) -> None:
    click.echo(f"Uploading: {path}")
    result = client.upload_file_to_admin_in_container(
        path, container=container, force_overwrite=force
    )
    if result.get("ok"):
        size = result.get("size") or 0
        click.echo(
            f"✓ Uploaded {path.name} ({size / (1024 * 1024):.2f} MB) → {result.get('remote_path')}"
        )
        click.echo("Completed: 1/1 successful")
    else:
        _err(f"{path.name}: {result.get('error')}")
        click.echo("Completed: 0/1 successful")
        raise SystemExit(1)


def _upload_many(client, files: list[Path], container: str, force: bool) -> None:
    ok = 0
    total = len(files)
    for f in files:
        r = client.upload_file_to_admin_in_container(
            f, container=container, force_overwrite=force
        )
        if r.get("ok"):
            size = r.get("size") or 0
            click.echo(f"  ✓ {f.name} ({size / (1024 * 1024):.2f} MB)")
            ok += 1
        else:
            click.echo(f"  ✗ {f.name}: {r.get('error')}")
    click.echo(f"Completed: {ok}/{total} successful")
    if ok != total:
        raise SystemExit(1)


def _err(msg: str) -> None:
    click.secho(msg, fg="red", err=True)


def _interactive_menu(ctx: click.Context) -> None:
    """Interactive menu using arrow-key selection if available."""
    try:
        import questionary  # type: ignore

        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Upload from src/output dir",
                "Upload files from provided directory(ies)",
                "Upload file from provided path(s)",
                "Download all .pb files from the server",
                "List all .pb files on the server",
                "List depreciated .pb files on the server",
                "Test SSH connection",
                "Exit",
            ],
            qmark="›",
            pointer="➤",
        ).ask()

        if choice == "Upload files from provided directory(ies)":
            raw = questionary.text(
                "Enter directory path(s), separated by space or comma"
            ).ask()
            dirs = _parse_multi(raw or "")
            if not dirs:
                click.echo("No directories provided. Aborting.")
                return
            container = _ensure_container(None)
            if not container:
                container = questionary.text(
                    "Docker container name (SSH_DOCKER_CONTAINER)",
                    default=os.environ.get("SSH_DOCKER_CONTAINER", ""),
                ).ask()
            force = questionary.confirm(
                "Overwrite existing files if present?", default=False
            ).ask()
            ctx.invoke(
                upload_dirs_cmd,
                dirs=tuple(dirs),
                force=bool(force),
                container=container,
            )
        elif choice == "Upload file from provided path(s)":
            raw = questionary.text(
                "Enter path(s) or glob pattern(s), separated by space or comma"
            ).ask()
            paths = _parse_multi(raw or "")
            if not paths:
                click.echo("No paths provided. Aborting.")
                return
            container = _ensure_container(None)
            if not container:
                container = questionary.text(
                    "Docker container name (SSH_DOCKER_CONTAINER)",
                    default=os.environ.get("SSH_DOCKER_CONTAINER", ""),
                ).ask()
            force = questionary.confirm(
                "Overwrite existing files if present?", default=False
            ).ask()
            ctx.invoke(
                upload_paths_cmd,
                paths=tuple(paths),
                force=bool(force),
                container=container,
            )
        elif choice == "Upload from src/output dir":
            container = _ensure_container(None)
            if not container:
                container = questionary.text(
                    "Docker container name (SSH_DOCKER_CONTAINER)",
                    default=os.environ.get("SSH_DOCKER_CONTAINER", ""),
                ).ask()
            ctx.invoke(upload_all_cmd, force=False, container=container)
        elif choice == "Download all .pb files from the server":
            # Ask destination optionally
            default_dest = str(DEFAULT_DOWNLOAD_DIR)
            dest_text = questionary.text(
                "Local destination directory (leave empty for default)",
                default=default_dest,
            ).ask()
            dest = Path(dest_text or default_dest)
            which = questionary.select(
                "Which remote directory to download?",
                choices=["all", "pb_files", "pb_files_depreciated"],
                default="all",
            ).ask()
            recursive = questionary.confirm(
                "Recurse into subdirectories?", default=True
            ).ask()
            force = questionary.confirm(
                "Overwrite existing local files if present?", default=False
            ).ask()
            ctx.invoke(
                download_all_cmd,
                directory=which,
                dest=dest,
                force=bool(force),
                recursive=bool(recursive),
            )
        elif choice == "List all .pb files on the server":
            ctx.invoke(list_cmd, directory="all")
        elif choice == "List depreciated .pb files on the server":
            ctx.invoke(list_cmd, directory="pb_files_depreciated")
        elif choice == "Test SSH connection":
            host = ctx.obj.get("host")
            # Show connection prints; avoid extra command prints
            try:
                client = _get_client(host)
                client.connect()
                click.echo("connection correct")
            except SSHClientError as e:
                _err(str(e))
            except Exception as e:
                _err(f"Unexpected error: {e}")
            finally:
                try:
                    client.disconnect()
                except Exception:
                    pass
        else:
            click.echo("Bye")

    except Exception:
        # Fallback to simple numbered prompts if questionary is not available
        click.echo("\nWhat would you like to do?")
        click.echo("  1) Upload from src/output dir")
        click.echo("  2) Upload files from provided directory(ies)")
        click.echo("  3) Upload file from provided path(s)")
        click.echo("  4) Download all .pb files from the server")
        click.echo("  5) List all .pb files on the server")
        click.echo("  6) List depreciated .pb files on the server")
        click.echo("  7) Test SSH connection")
        click.echo("  8) Exit")

        choice = click.prompt("Select option", type=int, default=1)
        if choice == 1:
            container = _ensure_container(None)
            if not container:
                container = click.prompt(
                    "Docker container name (SSH_DOCKER_CONTAINER)", type=str
                )
            ctx.invoke(upload_all_cmd, force=False, container=container)
        elif choice == 2:
            raw = click.prompt(
                "Enter directory path(s), separated by space or comma", type=str
            )
            dirs = _parse_multi(raw)
            container = _ensure_container(None)
            if not container:
                container = click.prompt(
                    "Docker container name (SSH_DOCKER_CONTAINER)", type=str
                )
            force = click.confirm("Overwrite existing files if present?", default=False)
            ctx.invoke(
                upload_dirs_cmd, dirs=tuple(dirs), force=force, container=container
            )
        elif choice == 3:
            raw = click.prompt(
                "Enter path(s) or glob pattern(s), separated by space or comma",
                type=str,
            )
            paths = _parse_multi(raw)
            container = _ensure_container(None)
            if not container:
                container = click.prompt(
                    "Docker container name (SSH_DOCKER_CONTAINER)", type=str
                )
            force = click.confirm("Overwrite existing files if present?", default=False)
            ctx.invoke(
                upload_paths_cmd, paths=tuple(paths), force=force, container=container
            )
        elif choice == 4:
            dest = Path(
                click.prompt(
                    "Local destination directory", default=str(DEFAULT_DOWNLOAD_DIR)
                )
            )
            which = click.prompt(
                "Which remote directory to download? (all/pb_files/pb_files_depreciated)",
                type=click.Choice(
                    ["all", "pb_files", "pb_files_depreciated"], case_sensitive=False
                ),
                default="all",
            )
            recursive = click.confirm("Recurse into subdirectories?", default=True)
            force = click.confirm(
                "Overwrite existing local files if present?", default=False
            )
            ctx.invoke(
                download_all_cmd,
                directory=which,
                dest=dest,
                force=force,
                recursive=recursive,
            )
        elif choice == 5:
            ctx.invoke(list_cmd, directory="all")
        elif choice == 6:
            ctx.invoke(list_cmd, directory="pb_files_depreciated")
        elif choice == 7:
            # Test connection with visible connection prints
            host = ctx.obj.get("host")
            try:
                client = _get_client(host)
                client.connect()
                click.echo("connection correct")
            except SSHClientError as e:
                _err(str(e))
            except Exception as e:
                _err(f"Unexpected error: {e}")
            finally:
                try:
                    client.disconnect()
                except Exception:
                    pass
        else:
            click.echo("Bye")


if __name__ == "__main__":
    cli()
