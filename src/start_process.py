import glob
import json

from pabulib.checker import Checker  # noqa: F401

import helpers.utilities as utils
from helpers.settings import output_path
from helpers.utilities import create_logger
from process_data.run_it import run_it

settings = {"year": 2026}

logger = create_logger()

city = "Warszawa"
# city = "Łódź"
# city = "Poznań"
# city = "Gdynia"
# city = "mechanical_turk"
# city = "stanford"
# city = "Lublin"
# city = "Wrocław"
# city = "Kraków"
# city = "Katowice"
# city = "Częstochowa"

settings["unit"] = city


# GET DATA
logger.info(f'{city}, year: {settings["year"]}, starting the process...')
run_it(**settings)
logger.info(f'{city}, year: {settings["year"]}, process of getting data finished.')

# CHECK IF DATA IS CORRECT, count votes per project
# pass which files to check, default: all .pb's in output directory

files_in_output_dir = "*"
# files_in_output_dir = "Poland_Warszawa_*"
# files_in_output_dir = "/cleaned/*"

path_to_all_files = f"{output_path}/{files_in_output_dir}.pb"

files = glob.glob(path_to_all_files)
utils.human_sorting(files)
checker = Checker()
results = checker.process_files(files)


# print(json.dumps(results["summary"], indent=4, ensure_ascii=False))

# print(json.dumps(results["metadata"], indent=4, ensure_ascii=False))

# print(json.dumps(results, indent=4, ensure_ascii=False))

# Filter out files where 'results' is "File looks correct!"
filtered_results = {
    key: value
    for key, value in results.items()
    if not (isinstance(value, dict) and value.get("results") == "File looks correct!")
}

# Print the filtered JSON
print(json.dumps(filtered_results, indent=4))
