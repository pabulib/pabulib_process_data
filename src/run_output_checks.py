"""Check if .pb file(s) is correct.

This script loads .pb files and checks if data in file is consistent
Among other things, it checks:
    if commas in floats
    if sum of selected project costs is not higher than budget
    if number of votes in VOTES is the same as counted in PROJECTS
    if projects number in META is the same as counted in PROJECTS
    if max vote length is exceeded
    if projects with no votes (which is not bad right away but suspicious)
    if points: check if scores in PROJECST equals counted in VOTES

Pass which files to check.
You can select
    files_in_output_dir: str
        if '*' : all files in output dir
        if '/cleaned/*' all files in output/cleaned dir
        if 'Poland_Katowice_2021_*' just matching files
    files_in_absolute_dir: str
        or provide your own absolute path to dir with .pb files to check
    create_txt_report: bool
        if set to True will save output report to .txt file
"""

from helpers.output_check import CheckOutputFiles  # noqa: F401

params = {
    # all files in output path
    # "files_in_output_dir": "*",
    # just selected files
    "files_in_output_dir": "Poland_Warszawa_*",
    # just files in output/cleaned dir
    # "files_in_output_dir": "/cleaned/*",
    # provide your own absolute path (remember about `*` to match all files)
    # "files_in_absolute_dir": "/*",
    # save output to txt file
    "create_txt_report": False,
}

cof = CheckOutputFiles(**params)
cof.check_output_files()
