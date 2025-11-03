# SSH client

Click-based helper to list and upload `.pb` files to the remote server and into the Admin-panel upload directory (inside a Docker container).

## Run it

- Interactive menu:
  - `python src/ssh_client/click_cli.py`

- Common commands:
  - `python src/ssh_client/click_cli.py list`
  - `python src/ssh_client/click_cli.py list --dir pb_files`
  - `python src/ssh_client/click_cli.py list --dir pb_files_depreciated`
  - `python src/ssh_client/click_cli.py download-all` (downloads all `.pb` recursively to `src/ssh_client/downloads` by default)
  - `python src/ssh_client/click_cli.py download-all --dir pb_files --dest path/to/local/dir --no-recursive` (choose source dir/dest and disable recursion)
  - `python src/ssh_client/click_cli.py upload <file_or_dir>`
  - `python src/ssh_client/click_cli.py upload-paths <path_or_glob> [<path_or_glob> ...]`
  - `python src/ssh_client/click_cli.py upload-dirs <dir> [<dir> ...]`
  - `python src/ssh_client/click_cli.py upload-all` (uploads all `.pb` from `src/output` with confirmation)
  - With SSH config host: `python src/ssh_client/click_cli.py --host <name> list`
  - With container override: `python src/ssh_client/click_cli.py --host <name> upload-all --container <container>`

## Configuration

Configuration is read in this order (later overrides earlier):
1. Repository `.env` (project root)
2. `src/ssh_client/.env` (local overrides for this tool)
3. SSH config host provided via `--host` or `SSH_CONFIG_HOST` (uses `~/.ssh/config`)
4. Direct environment variables

### Environment variables

- SSH connection:
  - `SSH_HOST`, `SSH_USERNAME`, `SSH_PASSWORD` (or `SSH_KEY_PATH`), `SSH_PORT`
  - Or use `--host <name>` to load from `~/.ssh/config` (equivalent to setting `SSH_CONFIG_HOST`)
- Remote directories (defaults are sensible for the current server layout):
  - `SSH_REMOTE_PB_FILES_DIR` (default: `/home/pabulib/pb_files`)
  - `SSH_REMOTE_PB_DEPRECIATED_DIR` (default: `/home/pabulib/pb_files_depreciated`)
- Admin uploads inside Docker container:
  - `SSH_DOCKER_CONTAINER` (required for uploads)
  - `SSH_CONTAINER_UPLOAD_TMP_DIR` (default: `/tmp/pabulib_uploads`)

You can copy `.env.example` to `.env` and adjust values. A separate `src/ssh_client/.env` may be used for local overrides.
