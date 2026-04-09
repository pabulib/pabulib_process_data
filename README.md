# Pabulib

Pabulib is an open <b>PA</b>rticipatory <b>BU</b>dgeting <b>LIB</b>rary. Project collects the participatory budgeting data from all over the world. In a [companion paper](http://pabulib.org/format) we have introduced universal .pb data format in which we store all the files.

http://pabulib.org

<br>

### <b>NOTE</b>
This repository is still in "work in progress" mode: at the beginnig we wrote the code just for ourselves. Now we need to beautify this to make it understandable and usable for everyone. We will do it, just give us some time :) Till then we think that even in such not-perfect format it could be useful for someone. If something is unclear just contact us! <pabulib@uj.edu.pl>

Authors

<br>


## Usage
<br>

### Environment
```
python -m venv venv
pip install -r requirements.txt
```

### Checker

NOTE: The checker is currently in deployment/testing mode. If there are changes in Checker repo (which happens quite often), you must reinstall it to apply the latest updates.

To install the checker:

```bash
pip install pabulib-checker
```

To update to the latest version:

```bash
pip install --upgrade pabulib-checker
```


### Process the data (from csv, excel, pdf):
```
1. add data to data/<city> directory
2. add all needed scritps to process_data/cities/<city>
    settings.py and budgets.py are obligatory, please check `cities/a_city_template` dir as a reference
3. run the process. Choose year and the city in the script and run it:
    start_process.py
```

### Dual-source data policy

Some cities send two separate sources at once:

- a projects sheet with official totals per project,
- a votes sheet with anonymized ballots.

If these two sources disagree, do not silently replace the project-level totals
with values recomputed from the ballots. The default interpretation should be:

- `PROJECTS` follows the official projects/results source,
- `VOTES` follows the anonymized ballots source,
- any mismatch between the two should remain visible and be documented.

If a city really requires recomputing project totals from ballots, make that an
explicit city-level decision in `settings.py` or a custom city pipeline.

### Example processing run
To better understand how the pipeline works, you can use the provided example template. This example processes a fictional city (a_city_template) for the year 2025 and generates .pb files based on example data:

just run
```
python start_process_template.py
```

and see the results in `output` directory!

### Check if output .pb files are correct
```
1. set in params path to .pb files you want to check:
    to check all files in output directory:
        "files_in_output_dir": "*"
    or in provided absolute path:
        "files_in_absolute_dir": "/*" (remember about `*` to match all files)
2. run output checks:
    python run_output_checks.py
```

### Modify .pb files: for example to count votes or to change columns order
```
modify_pb_files.py
```
if `self.modified` is changed to `True`, new file will be saved in `output/cleaned` directory.

### Visualize, play with data:
```
src/analytics/test.ipynb
```

## SSH client: list and upload pb files

Convenient CLI to interact with the remote PB files server and Admin uploads. First, install deps (once):

```bash
pip install -r requirements.txt
```

Then use the Click CLI:

```bash
# List remote files (both published and archived)
python src/ssh_client/click_cli.py list

# Upload all .pb files produced locally (from src/output)
python src/ssh_client/click_cli.py upload-all

# Upload a specific file or a whole directory
python src/ssh_client/click_cli.py upload path/to/file.pb
python src/ssh_client/click_cli.py upload path/to/dir

# Upload multiple paths (files or glob patterns)
python src/ssh_client/click_cli.py upload-paths path/to/*.pb other/file.pb

# Upload all .pb files from multiple directories
python src/ssh_client/click_cli.py upload-dirs src/output another/dir
```

Tip: set SSH connection details in `.env` (or use `--host` to reference an entry in `~/.ssh/config`). For Admin uploads, set `SSH_DOCKER_CONTAINER` so the Admin UI can see the uploaded files inside the container.
