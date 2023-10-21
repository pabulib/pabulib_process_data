from process_data.run_it import run_it
from helpers.output_check import CheckOutputFiles  # noqa: F401
from helpers.utilities import create_logger

settings = {
    "year": 2020,
    "scrape_data": True,
    # "preprocessing": False
}

logger = create_logger()

# city = "Warszawa"
# city = "Łódź"
# city = "Poznań"
# city = "Gdynia"
# city = "mechanical_turk"
city = "Lublin"
# city = "Wrocław"

settings["unit"] = city


# GET DATA
logger.info(f'{city}, year: {settings["year"]}, starting the process...')
run_it(**settings)
logger.info(
    f'{city}, year: {settings["year"]}, process of getting data finished.')

# CHECK IF DATA IS CORRECT, count votes per project
# pass which files to check, default: all .pb's in output directory

# files_to_check = 'Poland_Katowice_2021_*'
files_to_check = "*"
# files_to_check = f'poland_{city}_{settings["year"]}_*'

logger.info(
    f'City: {city}, year: {settings["year"]}, '
    f'checking output files for {files_to_check}.'
)
cof = CheckOutputFiles(files_to_check)
cof.check_output_files()
