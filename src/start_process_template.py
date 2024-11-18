# ============================================================
# EXAMPLE CONFIGURATION
# ============================================================
# To run the processing for a specific city and year, uncomment
# lines in start_process.py and ensure no other city is uncommented.
#
# This file is a template to show to process pipeline looks,
# with example data. In data/a_city_template/2025 directory
# you will find two sample Excels in a format as we usally get
# from cities: projects and votes.
#
# In process_data/cities/a_city_template you will find two
# configuration files that we use to process these data.
# Please check it out, it's a bit documented. Based on
# settings in there, .pb files will be created.
# ============================================================

from helpers.output_check import CheckOutputFiles  # noqa: F401
from helpers.utilities import create_logger
from process_data.run_it import run_it

logger = create_logger()

# Configuration settings for the year and city
settings = {"year": 2025, "unit": "a_city_template"}

# GET DATA FROM EXCEL FILES AND SAVE NEW .PB FILES
run_it(**settings)

# CHECK IF DATA IN PRODUCED .PB FILES IS CORRECT
files_to_check = "*"
cof = CheckOutputFiles(files_to_check)
cof.check_output_files()

# ============================================================
# NOTE: Once you will run this script, it will generate three
# .pb files in output directory:
#   - Poland_a_city_template_2025_.pb (for citywide)
#   - Poland_a_city_template_2025_DISTRICT_1.pb
#   - Poland_a_city_template_2025_DISTRICT_2.pb
# Please check them out!
# ============================================================
