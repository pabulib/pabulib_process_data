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

import glob
import json

from pabulib.checker import Checker

import helpers.utilities as utils
from helpers.settings import output_path

files_in_output_dir = "*"
# files_in_output_dir = "Poland_Warszawa_*"
# files_in_output_dir = "/cleaned/*"

path_to_all_files = f"{output_path}/{files_in_output_dir}.pb"

# path_to_all_files = (
#     "/Users/gignac/Desktop/Projects/pabulib_process_data/src/analytics/pb_files/*.pb"
# )

files = glob.glob(path_to_all_files)
utils.human_sorting(files)
checker = Checker()
results = checker.process_files(files)

# PRINT JUST SUMMARY
# print(json.dumps(results["summary"], indent=4))

# PRINT JUST METADATA
# print(json.dumps(results["metadata"], indent=4))

# PRINT ALL
# print(json.dumps(results, indent=4))

# PRINT ALL WITHOUT VALID FILES
# Filter out files where 'results' is "File looks correct!"
filtered_results = {
    key: value
    for key, value in results.items()
    if not (isinstance(value, dict) and value.get("results") == "File looks correct!")
}

# Print the filtered JSON
print(json.dumps(filtered_results, indent=4))


# save it to file
# with open("errors.txt", "w") as file:
#     json.dump(filtered_results, file, indent=4)
