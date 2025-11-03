"""
Standalone SSH Client for managing remote PB files.

This module provides functionality to connect to a remote server via SSH
and perform file operations on pb_files and pb_files_depreciated directories.

Configuration resolution priority:
1) Direct parameters
2) Environment variables (including values loaded from .env)
3) ~/.ssh/config (when a host is provided or SSH_CONFIG_HOST is set)

Notes
- The remote directory name uses the project-specific spelling
    "pb_files_depreciated". This is intentional and must not be changed here.
"""

import os
import shlex
import stat
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

try:
    import paramiko

    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


class SSHClientError(Exception):
    """Custom exception for SSH client errors."""


def parse_ssh_config(host: str) -> Dict[str, str]:
    """Parse SSH config file for host configuration."""
    ssh_config_path = Path.home() / ".ssh" / "config"
    config = {}

    if not ssh_config_path.exists():
        return config

    try:
        ssh_config = paramiko.SSHConfig()
        with open(ssh_config_path, "r") as f:
            ssh_config.parse(f)

        host_config = ssh_config.lookup(host)

        # Map SSH config keys to our format
        if "hostname" in host_config:
            config["host"] = host_config["hostname"]
        if "port" in host_config:
            config["port"] = str(host_config["port"])
        if "user" in host_config:
            config["username"] = host_config["user"]
        if "identityfile" in host_config:
            # Take the first identity file and expand the path
            identity_files = host_config["identityfile"]
            if isinstance(identity_files, list):
                config["key_path"] = str(Path(identity_files[0]).expanduser())
            else:
                config["key_path"] = str(Path(identity_files).expanduser())

    except Exception as e:
        print(f"Warning: Could not parse SSH config: {e}")

    return config


class SSHClient:
    """Standalone SSH client for remote server operations."""

    def __init__(
        self,
        host: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22,
        remote_pb_files_dir: Optional[str] = None,
        remote_pb_depreciated_dir: Optional[str] = None,
    ) -> None:
        """
        Initialize SSH client with configuration.

        Priority order for configuration:
        1. Direct parameters
        2. Environment variables
        3. SSH config file

        Args:
            host: SSH hostname or IP
            username: SSH username
            password: SSH password (not recommended, use key_path instead)
            key_path: Path to SSH private key
            port: SSH port (default: 22)
            remote_pb_files_dir: Remote pb_files directory path
            remote_pb_depreciated_dir: Remote pb_files_depreciated directory path
        """
        self._client: Optional[paramiko.SSHClient] = None
        self._sftp: Optional[paramiko.SFTPClient] = None
        self._connected = False

        if not PARAMIKO_AVAILABLE:
            raise SSHClientError(
                "paramiko library not installed. Run: pip install paramiko"
            )

        # 1. Start with direct parameters
        self.host = host
        self.username = username
        self.password = password
        self.key_path = key_path
        self.port = port
        self.remote_pb_files_dir = remote_pb_files_dir
        self.remote_pb_depreciated_dir = remote_pb_depreciated_dir

        # Container related settings (Admin uploads are handled inside container)
        self.docker_container: Optional[str] = os.environ.get("SSH_DOCKER_CONTAINER")
        self.container_upload_tmp_dir: str = os.environ.get(
            "SSH_CONTAINER_UPLOAD_TMP_DIR", "/tmp/pabulib_uploads"
        )

        # 2. Fill in missing values from environment variables
        ssh_config_host = os.environ.get("SSH_CONFIG_HOST")

        if not self.host:
            self.host = os.environ.get("SSH_HOST")
        if not self.username:
            self.username = os.environ.get("SSH_USERNAME")
        if not self.password:
            self.password = os.environ.get("SSH_PASSWORD")
        if not self.key_path:
            self.key_path = os.environ.get("SSH_KEY_PATH")
        if not self.port or self.port == 22:
            self.port = int(os.environ.get("SSH_PORT", "22"))
        if not self.remote_pb_files_dir:
            self.remote_pb_files_dir = os.environ.get(
                "SSH_REMOTE_PB_FILES_DIR", "/home/pabulib/pb_files"
            )
        if not self.remote_pb_depreciated_dir:
            self.remote_pb_depreciated_dir = os.environ.get(
                "SSH_REMOTE_PB_DEPRECIATED_DIR", "/home/pabulib/pb_files_depreciated"
            )

        # Container settings are already set above; no additional fallback is required.

        # 3. Try SSH config file if we have SSH_CONFIG_HOST or missing connection details
        config_host_to_use = ssh_config_host or self.host
        if config_host_to_use and (
            not self.username
            or (not self.password and not self.key_path)
            or ssh_config_host
        ):
            ssh_config = parse_ssh_config(config_host_to_use)

            # If using SSH_CONFIG_HOST, prioritize config values
            if ssh_config_host:
                if "host" in ssh_config:
                    self.host = ssh_config["host"]
                if "username" in ssh_config:
                    self.username = ssh_config["username"]
                if "key_path" in ssh_config:
                    self.key_path = ssh_config["key_path"]
                if "port" in ssh_config:
                    self.port = int(ssh_config["port"])
            else:
                # Fill in missing values from SSH config
                if not self.username and "username" in ssh_config:
                    self.username = ssh_config["username"]
                if not self.key_path and "key_path" in ssh_config:
                    self.key_path = ssh_config["key_path"]
                if "host" in ssh_config:
                    self.host = ssh_config[
                        "host"
                    ]  # hostname from config might be different
                if "port" in ssh_config:
                    self.port = int(ssh_config["port"])

        # Expand user paths
        if self.key_path:
            self.key_path = str(Path(self.key_path).expanduser())

        # If no specific key path but we have a username, try default SSH key locations
        if not self.key_path and not self.password and self.username:
            default_keys = [
                "~/.ssh/id_ed25519",
                "~/.ssh/id_rsa",
                "~/.ssh/id_ecdsa",
                "~/.ssh/id_dsa",
            ]
            for key_path in default_keys:
                expanded_path = Path(key_path).expanduser()
                if expanded_path.exists():
                    self.key_path = str(expanded_path)
                    print(f"Using default SSH key: {self.key_path}")
                    break

        # Validation
        if not self.host:
            raise SSHClientError(
                "SSH host is required. Set SSH_HOST environment variable or pass 'host' parameter."
            )
        if not self.username:
            raise SSHClientError(
                "SSH username is required. Set SSH_USERNAME environment variable or pass 'username' parameter."
            )
        if not self.password and not self.key_path:
            raise SSHClientError(
                "Either SSH password or key path is required. Set SSH_PASSWORD/SSH_KEY_PATH environment variables or pass parameters."
            )
        if self.key_path and not Path(self.key_path).exists():
            raise SSHClientError(f"SSH key file not found: {self.key_path}")

    def connect(self) -> bool:
        """
        Establish SSH connection to the remote server.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            SSHClientError: If connection fails
        """
        if self._connected:
            return True

        try:
            self._client = paramiko.SSHClient()
            self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            print(f"Connecting to {self.username}@{self.host}:{self.port}")

            # Determine authentication method
            if self.key_path and Path(self.key_path).exists():
                # Use SSH key authentication
                print(f"Using SSH key: {self.key_path}")
                self._client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_path,
                    timeout=30,
                )
            elif self.password:
                # Use password authentication
                print("Using password authentication")
                self._client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=30,
                )
            else:
                raise SSHClientError(
                    "Either SSH_PASSWORD or SSH_KEY_PATH must be provided"
                )

            # Initialize SFTP client
            self._sftp = self._client.open_sftp()
            self._connected = True

            print("✓ SSH connection established")
            return True

        except Exception as e:
            self._cleanup()
            raise SSHClientError(f"Failed to connect to {self.host}: {str(e)}")

    def disconnect(self) -> None:
        """Close SSH connection and cleanup resources."""
        self._cleanup()
        print("SSH connection closed")

    def _cleanup(self) -> None:
        """Internal cleanup method."""
        if self._sftp:
            try:
                self._sftp.close()
            except:
                pass
            self._sftp = None

        if self._client:
            try:
                self._client.close()
            except:
                pass
            self._client = None

        self._connected = False

    def _ensure_connected(self) -> None:
        """Ensure SSH connection is active."""
        if not self._connected:
            self.connect()

    def _list_pb_files_in_dir(
        self, remote_dir: str
    ) -> List[Dict[str, Union[str, int, datetime]]]:
        """Internal helper to list .pb files in a given remote directory."""
        self._ensure_connected()
        try:
            files: List[Dict[str, Union[str, int, datetime]]] = []
            assert self._sftp is not None  # for type checkers
            file_list = self._sftp.listdir_attr(remote_dir)
            for fa in file_list:
                if fa.filename.endswith(".pb") and stat.S_ISREG(fa.st_mode):
                    files.append(
                        {
                            "name": fa.filename,
                            "size": fa.st_size,
                            "modified": datetime.fromtimestamp(fa.st_mtime),
                            "path": f"{remote_dir}/{fa.filename}",
                        }
                    )
            return sorted(files, key=lambda x: x["name"])  # type: ignore[index]
        except Exception as e:
            raise SSHClientError(f"Failed to list files in {remote_dir}: {str(e)}")

    def list_pb_files(self) -> List[Dict[str, Union[str, int, datetime]]]:
        """
        List all .pb files in the remote pb_files directory on the host.

        Returns:
            List of dicts with: name, size, modified, path
        """
        try:
            assert self.remote_pb_files_dir is not None
            return self._list_pb_files_in_dir(self.remote_pb_files_dir)
        except Exception as e:
            raise SSHClientError(f"Failed to list pb_files: {str(e)}")

    def list_pb_depreciated_files(self) -> List[Dict[str, Union[str, int, datetime]]]:
        """
        List all .pb files in the remote pb_files_depreciated directory on the host.

        Returns:
            List of dicts with: name, size, modified, path
        """
        try:
            assert self.remote_pb_depreciated_dir is not None
            return self._list_pb_files_in_dir(self.remote_pb_depreciated_dir)
        except Exception as e:
            raise SSHClientError(f"Failed to list pb_files_depreciated: {str(e)}")

    def list_all_pb_files(
        self,
    ) -> Dict[str, List[Dict[str, Union[str, int, datetime]]]]:
        """
        List .pb files from both pb_files and pb_files_depreciated.

        Returns:
            Dict with keys 'pb_files' and 'pb_files_depreciated'
        """
        return {
            "pb_files": self.list_pb_files(),
            "pb_files_depreciated": self.list_pb_depreciated_files(),
        }

    # ----------
    # Recursive
    # ----------

    def _walk_remote_pb_files(
        self, remote_dir: str
    ) -> List[Dict[str, Union[str, int, datetime]]]:
        """
        Recursively walk a remote directory and collect .pb files with metadata.

        Returns list with keys: name, size, modified, path
        """
        self._ensure_connected()
        assert self._sftp is not None
        out: List[Dict[str, Union[str, int, datetime]]] = []

        stack = [remote_dir.rstrip("/")]
        visited = set()
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            try:
                entries = self._sftp.listdir_attr(current)
            except FileNotFoundError:
                continue
            except Exception as e:
                raise SSHClientError(f"Failed to list {current}: {e}")

            for fa in entries:
                name = fa.filename
                full_path = f"{current}/{name}"
                mode = fa.st_mode
                if stat.S_ISDIR(mode):
                    stack.append(full_path)
                elif stat.S_ISREG(mode) and name.endswith(".pb"):
                    out.append(
                        {
                            "name": name,
                            "size": fa.st_size,
                            "modified": datetime.fromtimestamp(fa.st_mtime),
                            "path": full_path,
                        }
                    )

        return sorted(out, key=lambda x: x["path"])  # type: ignore[index]

    def list_pb_files_recursive(self) -> List[Dict[str, Union[str, int, datetime]]]:
        """Recursively list .pb files under the pb_files directory."""
        try:
            assert self.remote_pb_files_dir is not None
            return self._walk_remote_pb_files(self.remote_pb_files_dir)
        except Exception as e:
            raise SSHClientError(f"Failed to recursively list pb_files: {str(e)}")

    def list_pb_depreciated_files_recursive(
        self,
    ) -> List[Dict[str, Union[str, int, datetime]]]:
        """Recursively list .pb files under the pb_files_depreciated directory."""
        try:
            assert self.remote_pb_depreciated_dir is not None
            return self._walk_remote_pb_files(self.remote_pb_depreciated_dir)
        except Exception as e:
            raise SSHClientError(
                f"Failed to recursively list pb_files_depreciated: {str(e)}"
            )

    def download_file(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        overwrite: bool = False,
        preserve_mtime: bool = True,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Download a single remote file to a local path via SFTP.

        Args:
            remote_path: Full remote path to the file
            local_path: Destination local filepath
            overwrite: If False and local file exists, skip with error
            preserve_mtime: When True, preserve remote modification time

        Returns:
            Dict with keys: ok, error/message, local_path, size
        """
        self._ensure_connected()
        assert self._sftp is not None

        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        if local_path.exists() and not overwrite:
            return {
                "ok": False,
                "error": f"Local file already exists: {local_path}",
            }

        # Download to a temp file first for atomicity, then rename
        tmp_path = local_path.with_suffix(local_path.suffix + ".part")
        try:
            self._sftp.get(remote_path, str(tmp_path))
            # Determine size and mtime from remote
            st = self._sftp.stat(remote_path)
            size = int(getattr(st, "st_size", 0) or 0)

            # Move into place
            if local_path.exists():
                try:
                    local_path.unlink()
                except Exception:
                    pass
            tmp_path.replace(local_path)

            if preserve_mtime:
                try:
                    mtime = int(getattr(st, "st_mtime", 0) or 0)
                    os.utime(local_path, (mtime, mtime))
                except Exception:
                    pass

            return {
                "ok": True,
                "message": f"Downloaded to {local_path}",
                "local_path": str(local_path),
                "size": size,
            }
        except Exception as e:
            # Cleanup temp file
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except Exception:
                pass
            return {"ok": False, "error": f"Failed to download: {e}"}

    def get_file_info(
        self, filename: str, directory: str = "pb_files"
    ) -> Optional[Dict[str, Union[str, int, datetime]]]:
        """
        Get info for a specific file from pb_files or pb_files_depreciated.

        Args:
            filename: name of the .pb file
            directory: 'pb_files' or 'pb_files_depreciated'

        Returns:
            Dict with name, size, modified, path, directory — or None if not found
        """
        self._ensure_connected()

        remote_dir = (
            self.remote_pb_files_dir
            if directory == "pb_files"
            else self.remote_pb_depreciated_dir
        )
        remote_path = f"{remote_dir}/{filename}"

        try:
            st = self._sftp.stat(remote_path)
            return {
                "name": filename,
                "size": st.st_size,
                "modified": datetime.fromtimestamp(st.st_mtime),
                "path": remote_path,
                "directory": directory,
            }
        except FileNotFoundError:
            return None
        except Exception as e:
            raise SSHClientError(f"Failed to get file info for {filename}: {str(e)}")

    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """
        Execute a command on the remote server.

        Args:
            command: Command to execute

        Returns:
            Tuple of (stdout, stderr, exit_code)
        """
        self._ensure_connected()

        try:
            print(f"Executing: {command}")
            stdin, stdout, stderr = self._client.exec_command(command)
            exit_code = stdout.channel.recv_exit_status()

            stdout_data = stdout.read().decode("utf-8")
            stderr_data = stderr.read().decode("utf-8")

            return stdout_data, stderr_data, exit_code

        except Exception as e:
            raise SSHClientError(f"Failed to execute command '{command}': {str(e)}")

    def _docker_exec_stream_file(
        self, container: str, dest_path: str, local_path: Path
    ) -> Tuple[bool, str]:
        """
        Stream a local file into a file inside a docker container using docker exec on the remote host.

        Returns (ok, error_message)
        """
        self._ensure_connected()

        # Ensure destination directory exists inside container
        dest_dir = os.path.dirname(dest_path)
        mkdir_cmd = f"docker exec -i {shlex.quote(container)} sh -lc {shlex.quote(f'mkdir -p {dest_dir}')}"
        _, _, _ = self.execute_command(mkdir_cmd)

        # Prepare docker exec cat command
        cat_cmd = f"docker exec -i {shlex.quote(container)} sh -lc {shlex.quote(f'cat > {dest_path}')}"
        try:
            print(f"Executing (stream): {cat_cmd}")
            stdin, stdout, stderr = self._client.exec_command(cat_cmd)

            # Stream file content to stdin of remote command
            with open(local_path, "rb") as f:
                while True:
                    chunk = f.read(32768)
                    if not chunk:
                        break
                    stdin.channel.sendall(chunk)
            stdin.channel.shutdown_write()

            exit_code = stdout.channel.recv_exit_status()
            if exit_code != 0:
                err = stderr.read().decode("utf-8", errors="ignore")
                return (
                    False,
                    f"docker exec cat failed (exit {exit_code}): {err.strip()}",
                )
            return True, ""
        except Exception as e:
            return False, str(e)

    def _docker_path_exists(self, container: str, path: str) -> bool:
        """Check if a path exists inside container."""
        cmd = f"docker exec -i {shlex.quote(container)} sh -lc {shlex.quote(f'test -e {path}')}"
        _, _, exit_code = self.execute_command(cmd)
        return exit_code == 0

    def _docker_file_size(self, container: str, path: str) -> Optional[int]:
        """Return file size inside container using wc -c, or None on failure."""
        # Use POSIX-compatible method
        cmd = f"docker exec -i {shlex.quote(container)} sh -lc {shlex.quote(f'wc -c < {path}')}"
        out, err, exit_code = self.execute_command(cmd)
        if exit_code == 0:
            try:
                return int(out.strip())
            except Exception:
                return None
        return None

    def test_connection(self) -> Dict[str, Union[bool, str]]:
        """
        Test the SSH connection and return status information.

        Returns:
            Dictionary with connection status and server information
        """
        try:
            self.connect()

            # Get server info
            stdout, stderr, exit_code = self.execute_command(
                'uname -a && echo "---" && whoami && echo "---" && pwd'
            )

            return {"connected": True, "server_info": stdout.strip(), "error": None}

        except Exception as e:
            return {"connected": False, "server_info": None, "error": str(e)}

    def upload_file_to_admin_in_container(
        self,
        local_path: Union[str, Path],
        remote_filename: Optional[str] = None,
        container: Optional[str] = None,
        dest_dir: Optional[str] = None,
        force_overwrite: bool = False,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Upload a single .pb file into a Docker container's upload directory (Admin panel visible).

        Args:
            local_path: Path to local .pb file
            remote_filename: Optional remote filename (defaults to local filename)
            container: Docker container name (defaults to env SSH_DOCKER_CONTAINER)
            dest_dir: Path inside container (defaults to env SSH_CONTAINER_UPLOAD_TMP_DIR)
            force_overwrite: Overwrite existing file if present

        Returns:
            Dict with keys: ok, error/message, remote_path, size
        """
        self._ensure_connected()

        local_path = Path(local_path)
        if not local_path.exists():
            return {"ok": False, "error": f"Local file not found: {local_path}"}

        if not local_path.name.endswith(".pb"):
            return {"ok": False, "error": "Only .pb files are allowed"}

        remote_filename = remote_filename or local_path.name
        if not remote_filename.endswith(".pb"):
            remote_filename += ".pb"

        container = container or self.docker_container
        if not container:
            return {
                "ok": False,
                "error": "Docker container not specified (set SSH_DOCKER_CONTAINER or pass --container)",
            }

        dest_dir = dest_dir or self.container_upload_tmp_dir
        remote_path = f"{dest_dir.rstrip('/')}/{remote_filename}"

        # Check/handle overwrite
        if not force_overwrite and self._docker_path_exists(container, remote_path):
            return {
                "ok": False,
                "error": f"File already exists in container: {remote_filename}",
            }

        if force_overwrite and self._docker_path_exists(container, remote_path):
            rm_cmd = f"docker exec -i {shlex.quote(container)} sh -lc {shlex.quote(f'rm -f {remote_path}')}"
            _, err, exit_code = self.execute_command(rm_cmd)
            if exit_code != 0:
                return {
                    "ok": False,
                    "error": f"Failed to remove existing file: {err.strip()}",
                }

        ok, err = self._docker_exec_stream_file(container, remote_path, local_path)
        if not ok:
            return {"ok": False, "error": f"Upload via docker exec failed: {err}"}

        size = self._docker_file_size(container, remote_path)
        if size is None:
            return {
                "ok": True,
                "message": f"Uploaded {remote_filename} into container (size verification unavailable)",
                "remote_path": remote_path,
            }

        local_size = local_path.stat().st_size
        if size != local_size:
            return {
                "ok": False,
                "error": f"Upload verification failed: size mismatch (remote {size} vs local {local_size})",
            }

        return {
            "ok": True,
            "message": f"Successfully uploaded {remote_filename} into container",
            "remote_path": remote_path,
            "size": size,
        }

    def list_admin_uploads_in_container(
        self, container: Optional[str] = None, dest_dir: Optional[str] = None
    ) -> List[Dict[str, Union[str, int, datetime]]]:
        """
        List .pb files inside the container's admin upload directory.
        Returns a list of dicts: name, size, modified (when available), path.
        """
        self._ensure_connected()

        container = container or self.docker_container
        if not container:
            raise SSHClientError(
                "Docker container not specified (set SSH_DOCKER_CONTAINER or pass --container)"
            )
        dest_dir = dest_dir or self.container_upload_tmp_dir

        # Build a portable shell loop that prints name|size|mtime
        loop = (
            f"for f in {shlex.quote(dest_dir)}/*.pb; do "
            f'[ -f "$f" ] || continue; '
            f'b="$(basename "$f")"; '
            f's="$(wc -c < "$f" 2>/dev/null || echo 0)"; '
            # Try GNU stat first; fallback to date -r; else empty
            f'mt="$(stat -c %Y "$f" 2>/dev/null || date -r "$f" +%s 2>/dev/null || echo)"; '
            f'echo "$b|$s|$mt"; '
            f"done"
        )
        cmd = f"docker exec -i {shlex.quote(container)} sh -lc {shlex.quote(loop)}"
        out, err, code = self.execute_command(cmd)
        if code != 0:
            raise SSHClientError(f"Failed to list uploads in container: {err.strip()}")

        files: List[Dict[str, Union[str, int, datetime]]] = []
        for line in out.strip().splitlines():
            parts = line.strip().split("|")
            if len(parts) < 2:
                continue
            name = parts[0]
            try:
                size = int(parts[1])
            except Exception:
                size = 0
            modified_dt: Optional[datetime] = None
            if len(parts) >= 3 and parts[2].strip():
                try:
                    modified_dt = datetime.fromtimestamp(int(float(parts[2].strip())))
                except Exception:
                    modified_dt = None
            info: Dict[str, Union[str, int, datetime]] = {
                "name": name,
                "size": size,
                "path": f"{dest_dir.rstrip('/')}/{name}",
            }
            if modified_dt is not None:
                info["modified"] = modified_dt
            files.append(info)

        return sorted(files, key=lambda x: x["name"]) if files else []

    def clear_admin_uploads_in_container(
        self,
        confirm: bool = False,
        container: Optional[str] = None,
        dest_dir: Optional[str] = None,
    ) -> Dict[str, Union[bool, str, int]]:
        """
        Remove all .pb files from the container's admin upload directory.
        """
        if not confirm:
            return {"ok": False, "error": "Must set confirm=True to delete files"}

        self._ensure_connected()
        container = container or self.docker_container
        if not container:
            return {
                "ok": False,
                "error": "Docker container not specified (set SSH_DOCKER_CONTAINER or pass --container)",
            }
        dest_dir = dest_dir or self.container_upload_tmp_dir

        # Shell to count and remove files
        loop = (
            f"cnt=0; "
            f"for f in {shlex.quote(dest_dir)}/*.pb; do "
            f'[ -f "$f" ] || continue; '
            f'rm -f "$f" && cnt=$((cnt+1)); '
            f"done; echo $cnt"
        )
        cmd = f"docker exec -i {shlex.quote(container)} sh -lc {shlex.quote(loop)}"
        out, err, code = self.execute_command(cmd)
        if code != 0:
            return {"ok": False, "error": f"Failed to clear uploads: {err.strip()}"}
        try:
            deleted = int(out.strip() or "0")
        except Exception:
            deleted = 0
        return {"ok": True, "message": f"Deleted {deleted} files", "deleted": deleted}

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Convenience functions for standalone usage
def connect_from_env(**kwargs) -> "SSHClient":
    """Create SSH client using environment variables with optional overrides."""
    return SSHClient(**kwargs)


def connect_from_ssh_config(host: str, **kwargs) -> "SSHClient":
    """Create SSH client using SSH config file for the given host."""
    return SSHClient(host=host, **kwargs)


def quick_list_files(
    host: str = None, **kwargs
) -> Dict[str, List[Dict[str, Union[str, int, datetime]]]]:
    """
    Quick function to list all remote pb files.

    Args:
        host: SSH host (if None, uses environment variables)
        **kwargs: Additional SSH connection parameters

    Returns:
        Dictionary with file listings from both directories
    """
    if host:
        client = connect_from_ssh_config(host, **kwargs)
    else:
        client = connect_from_env(**kwargs)

    with client:
        return client.list_all_pb_files()


def quick_test_connection(host: str = None, **kwargs) -> Dict[str, Union[bool, str]]:
    """
    Quick function to test SSH connection.

    Args:
        host: SSH host (if None, uses environment variables)
        **kwargs: Additional SSH connection parameters

    Returns:
        Connection status information
    """
    try:
        if host:
            client = connect_from_ssh_config(host, **kwargs)
        else:
            client = connect_from_env(**kwargs)
        return client.test_connection()
    except Exception as e:
        return {"connected": False, "server_info": None, "error": str(e)}
