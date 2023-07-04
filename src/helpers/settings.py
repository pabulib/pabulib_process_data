import os


pabulib_dir = os.path.join(os.getcwd(), "src")
path_to_excel_files = os.path.join(pabulib_dir, "data")
output_path = os.path.join(pabulib_dir, "output")

logging_level = 'DEBUG'


def get_path_to_excel_files(city_dir_name, extra_dir=""):
    path_to_excel_files = os.path.join(
        pabulib_dir, "data", city_dir_name, extra_dir)
    return path_to_excel_files
