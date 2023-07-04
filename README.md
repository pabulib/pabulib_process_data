# Pabulib

Pabulib is an open <b>PA</b>rticipatory <b>BU</b>dgeting <b>LIB</b>rary. Project collects the participatory budgeting data from all over the world. In a [companion paper](http://pabulib.org/format) we have introduced universal .pb data format in which we store all the files.

http://pabulib.org

<br>

### <b>NOTE</b>
This repository is still in "work in progress" mode: at the beginnig we wrote a code just for ourselves. Now we need to beautify this it to make it understandable and usable for everyone. We will do it, just give as some time :) Till then we think that even in such format it could be useful for someone. If something is unclear just contact us!
<br>
Authors


## Usage
<br>

## Environment
```
python -m venv venv

```

### Process the data (from csv, excel, pdf):
```
1. add data to data/<city> directory
2. add all needed scritps to process_data/cities/<city>
    get_projects.py, budgets.py and settings.py are obligatory
3. run the process:
    start_process.py
```

### Check if output .pb files are correct
```
run_output_checks.py
```

### Modify .pb files: for example to count votes or to change columns order
```
modify_pb_files.py
```

### Visualize (WIP):
```
visualize.py
```