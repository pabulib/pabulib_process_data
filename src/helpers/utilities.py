import csv
import glob
import json
import os
import re
import sys
from collections import defaultdict

import numpy as np
import requests
import unidecode
import xlrd
from bs4 import BeautifulSoup as bs
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from xlsxwriter.workbook import Workbook

from helpers import settings

wrong_votes = (r"\N", "NULL", "---", "0", 0)


def count_projects_and_votes(path_to_file):
    remove_last_empty_line(path_to_file)
    with open(path_to_file, "r", encoding="utf-8") as file_:
        lines = file_.readlines()
        num_voters = 0
        # num_votes = 0
        num_projects = 0
        count_projects = True

        for line in lines:
            if count_projects:
                if str(line).startswith("PROJECTS\n") or str(line).startswith(
                    "project_id;"
                ):
                    continue
                if str(line) == "VOTES\n":
                    count_projects = False
                    continue
                num_projects += 1
            else:
                if str(line).startswith("voter_id;") or (not str(line)):
                    continue
                num_voters += 1

                # num_votes += len(line.split(';')[1].split(','))
    return num_projects, num_voters


def remove_last_empty_line(filename):
    with open(filename, encoding="utf-8") as f_input:
        data = f_input.read().rstrip("\n")
    with open(filename, "w", encoding="utf-8") as f_output:
        f_output.write(data)


def prepend_line_at_the_beggining_of_file(text, path_to_file):
    """Insert given string as a new line at the beginning of a file"""
    # define name of temporary dummy file
    dummy_file = path_to_file + ".bak"
    # open original file in read mode and dummy file in write mode
    with open(path_to_file, "r", encoding="utf-8") as read_obj, open(
        dummy_file, "w", encoding="utf-8"
    ) as write_obj:
        # Write given line to the dummy file
        write_obj.write(text)
        # Read lines from original file one by one
        # and append them to the dummy file
        for line in read_obj:
            write_obj.write(line)
    # remove original file
    os.remove(path_to_file)
    # Rename dummy file as the original file
    os.rename(dummy_file, path_to_file)


def get_soup(url):
    """Get soup from given url."""
    page = requests.get(
        url,
        # verify=False
    )
    soup = bs(page.content, "html.parser")
    return soup


def get_soup_requests_with(url):
    """Get soup from given url."""
    with requests.get(url, stream=True) as page:
        soup = bs(page.content, "html.parser")
        return soup


def remove_semicolon(text):
    """Remove semicolons as not to break if saved to CSV."""
    return text.replace(";", "")


def remove_quotes(text):
    """Remove quotes as not to break if saved to CSV."""
    return text.replace('"', "")


def remove_whitespaces(text):
    text = text.replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text


def clean_name(text):
    name = remove_quotes(text)
    name = remove_semicolon(name)
    name = remove_whitespaces(name)
    return name.strip()


def get_path_to_excel_file(excel_filename):
    excel_filename = f"{excel_filename}.xlsx"
    path_to_file = os.path.join(settings.path_to_excel_files, excel_filename).replace(
        "\\", "/"
    )
    return path_to_file


def get_path_to_file_by_unit(excel_filename, unit, extra_dir="", ext="xlsx"):
    path_to_excel_file = settings.get_path_to_excel_files(
        unit, extra_dir=extra_dir)
    excel_filename = f"{excel_filename}.{ext}"
    path_to_file = os.path.join(
        path_to_excel_file, excel_filename).replace("\\", "/")
    return path_to_file


def handle_xlrd_options():
    """AttributeError: 'ElementTree' object has no attribute 'getiterator'
    problem solved as described on stack:

    https://stackoverflow.com/questions/64264563/attributeerror-elementtree-
    object-has-no-attribute-getiterator-when-trying"""

    xlrd.xlsx.ensure_elementtree_imported(False, None)
    xlrd.xlsx.Element_has_iter = True


def get_workbook(path_to_excel):
    handle_xlrd_options()
    wb = xlrd.open_workbook(path_to_excel, encoding_override="utf-8")
    return wb


def open_excel_workbook(path_to_excel, index=0, name=None):
    """Open workbook based on given path to excel file."""
    wb = get_workbook(path_to_excel)
    if name:
        sheet = wb.sheet_by_name(name)
        return sheet
    sheet = wb.sheet_by_index(index)
    return sheet


def get_col_names_indexes(sheet, headers_row=0):
    """Get column names in given excel file."""
    col_names_indexes = {}
    for col_index in range(sheet.ncols):
        col_names_indexes[sheet.cell_value(headers_row, col_index)] = col_index
    return col_names_indexes


def get_cell_value_by_column(sheet, row, col_name):
    """Get cell value from a sheet by passed column name."""
    col = sheet[col_name]
    return sheet.cell_value(row, col)


def create_or_append_to_file(file_name, first_line):
    file_path = os.path.join(settings.output_path,
                             file_name).replace("\\", "/")
    file_ = open(file_path, "a+", encoding="utf-8")
    file_.write(first_line)
    return file_


def remove_accents_from_str(accented_string):
    unaccented_string = unidecode.unidecode(accented_string)
    return unaccented_string


def create_unit_file(unit_file_name):
    unit_file_name_ = f"{unit_file_name}_.pb"
    unit_file = create_or_append_to_file(unit_file_name_, "")
    return unit_file


def get_file_path(unit_file_name, district_upper):
    file_name = f"{unit_file_name}_{district_upper}.pb"
    file_path = os.path.join(settings.output_path,
                             file_name).replace("\\", "/")
    return file_path


def create_json_file_name(country, unit, year, file_name):
    return f"{country}_{unit}_{year}_{file_name}"


def save_dict_as_json(data_dict, file_name):
    path_to_file = os.path.join(settings.output_path, "jsons", file_name).replace(
        "\\", "/"
    )
    # Serializing json
    json_object = json.dumps(data_dict, indent=4, ensure_ascii=False)
    # Writing to sample.json
    with open(path_to_file + ".json", "w", encoding="utf-8") as outfile:
        outfile.write(json_object)


def name_and_load_dict_as_json(country, unit, year, name):
    file_name = create_json_file_name(country, unit, year, name)
    json_object = load_json_obj(file_name)
    return json_object


def load_json_obj(file_name):
    path_to_file = os.path.join(settings.output_path, "jsons", file_name).replace(
        "\\", "/"
    )
    # Opening JSON file
    with open(path_to_file + ".json", "r", encoding="utf-8") as openfile:
        # Reading from json file
        json_object = json.load(openfile)
    return json_object


def create_project_selected_mapping_by_district(file_name):
    project_selected_mapping = {}
    json_file = load_json_obj(file_name)
    for district, project_dicts in json_file.items():
        project_selected_mapping[district] = {}
        for project_dict in project_dicts:
            project_id = project_dict["id"]
            project_id = project_id.split(".")[2].split("/")[0]
            selected = project_dict["selected"]
            project_selected_mapping[district][project_id] = selected
    return project_selected_mapping


def create_project_selected_mapping(file_name):
    project_selected_mapping = {}
    json_file = load_json_obj(file_name)
    for district, project_dicts in json_file.items():
        for project_dict in project_dicts:
            project_id = project_dict["id"]
            project_selected_mapping[project_id] = project_dict["selected"]
    return project_selected_mapping


def check_if_json_files_in_output(country, unit, year, logger):
    output_json_files = settings.output_path.replace(
        "\\", "/") + "/jsons/*.json"
    names = [os.path.basename(x) for x in glob.glob(output_json_files)]
    file_beginning = f"{country}_{unit}_{str(year)}"
    for json_file in names:
        if json_file.startswith(file_beginning):
            logger.info(
                f"There is JSON file for {file_beginning} in output dir! "
                "Skipping scraping. If you want to scrape anyway, please "
                "remove JSON files."
            )
            return True


def remove_charmaps(string):
    string = string.replace("―", "-").replace("²", "2")
    return string


def clean_project_name(name):
    name = name.lower()
    name = clean_name(name)
    name = remove_accents_from_str(name)
    name = name.replace(" ", "")
    name = name.strip().rstrip(".")
    return name


def create_project_id_from_district(district, project_no):
    district = district.lower().strip()
    district = district.replace("-", "").replace(" ", "")
    project_id = f"{district}_{str(project_no)}"
    return project_id


def change_district_into_name(district):
    district = district.strip()
    district = remove_accents_from_str(district)
    district = district.upper()
    district = district.replace(" - ", "-")
    district = district.replace(". ", "_")
    district = district.replace(" ", "_")
    district = district.replace(".", "_")
    return district


def create_district_subdistrict_upper(district_upper, subdistrict):
    subdistrict = change_district_into_name(subdistrict)
    district_upper = f"{district_upper}_{subdistrict}"
    return district_upper


def get_path_to_file(unit_file_name, district=""):
    output_path = settings.output_path
    file_path = f"{unit_file_name}{district}.pb"
    path_to_file = os.path.join(output_path, file_path).replace("\\", "/")
    return path_to_file


def create_csv_file(unit_file_name, district=""):
    path_to_file = get_path_to_file(unit_file_name, district)
    file_ = open(path_to_file, "w", newline="", encoding="utf-8")
    csv_file = csv.writer(file_, delimiter=";")
    return file_, csv_file


def append_to_csv_file(unit_file_name, district=""):
    path_to_file = get_path_to_file(unit_file_name, district)
    file_ = open(path_to_file, "a+", newline="", encoding="utf-8")
    csv_file = csv.writer(file_, delimiter=";")
    return file_, csv_file


def clear_project_title(name):
    name = remove_semicolon(name)
    name = name.replace("\xa0", " ")
    name = remove_charmaps(name)
    name = remove_whitespaces(name)
    return name


def get_table_from_soup(soup, table_name):
    table = soup.find("table", attrs={"class": table_name})
    table_body = table.find("tbody")
    rows = table_body.find_all("tr")
    return rows


def create_logger(logger_level=None):
    """Create logger instance to logging instead of printing.

    Example of usage:

        logger = create_logger()
        logger.debug('This is a debug message')
        logger.info('This is an info message')
        logger.warning('This is a warning message')
        logger.error('This is an error message')
        logger.critical('This is a critical message')

        time format option : {time:YYYY-MM-DD HH:mm:ss.SSS}
    """
    if not logger_level:
        logger_level = settings.logging_level

    fmt = (
        "<green>{time:HH:mm:ss}</green> "
        "| Pabulib "
        "| <level>{level: <8}</level> "
        #    "| {file} " # filaname from which log is diplayed.
        "| <cyan>{name}</cyan>"
        ":<cyan>{function}</cyan>:"
        "<cyan>{line}</cyan> "
        "- <level>{message}</level>"
    )
    config = {
        "handlers": [
            {"sink": sys.stderr, "format": fmt, "level": logger_level},
        ],
    }
    logger.remove()  # All configured handlers are removed
    logger.configure(**config)
    return logger


def create_web_driver(path_to_chromedriver="./chromedriver"):
    service_obj = Service(path_to_chromedriver)
    driver = webdriver.Chrome(service=service_obj)
    return driver


def load_pb_file(pb_file, encoding="utf-8-sig"):
    with open(pb_file, "r", newline="", encoding=encoding) as csvfile:
        votes_in_projects, scores_in_projects = False, False
        meta, projects, votes = {}, {}, {}
        section = ""
        header = []
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            if row:
                if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
                    section = str(row[0]).strip().lower()
                    header = next(reader)
                elif section == "meta":
                    meta[row[0]] = row[1].strip()
                elif section == "projects":
                    if 'votes' in header:
                        votes_in_projects = True
                    if "score" in header:
                        scores_in_projects = True
                    projects[row[0]] = {}
                    for it, key in enumerate(header[1:]):
                        projects[row[0]][key.strip()] = row[it + 1].strip()
                elif section == "votes":
                    if votes.get(row[0]):
                        raise RuntimeError(f"Duplicated Voter ID!! {row[0]}")
                    votes[row[0]] = {}
                    for it, key in enumerate(header[1:]):
                        votes[row[0]][key.strip()] = row[it + 1].strip()
    return meta, projects, votes, votes_in_projects, scores_in_projects


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def human_sorting(list_to_sort):
    list_to_sort.sort(key=natural_keys)


def count_votes_per_project(votes):
    counted_votes = defaultdict(int)
    for _, vote in votes.items():
        # Vote strength, if not defined 1 is default
        vote_strength = vote.get("vote_strength", 1)
        projects = vote["vote"].split(",")
        for project in projects:
            counted_votes[project] += vote_strength
    return counted_votes


def create_points_based_on_vote_length(projects):
    points = []
    point = len(projects)
    for _ in projects:
        points.append(point)
        point -= 1
    return points


def count_points_per_project(votes):
    counted_scores = defaultdict(int)
    for _, vote in votes.items():
        # Vote strength, if not defined 1 is default
        projects = vote["vote"].split(",")
        try:
            points = vote["points"].split(",")
        except KeyError:
            points = create_points_based_on_vote_length(projects)
        for project, point in zip(projects, points):
            counted_scores[project] += int(point)
    return counted_scores


def get_cost_from_text(text):
    text = text.replace("zł", "")
    return float(text.replace(" ", "").replace(",", "."))


def make_cost_printable(cost):
    cost = float(cost)
    return str("{:.2f}".format(cost) if cost % 1 else int(cost))


def convert_csv_to_xl(path_to_csv, delimiter=";", excel_name=None, encoding="utf8"):
    if not excel_name:
        excel_name = path_to_csv[:-4] + ".xlsx"
    workbook = Workbook(excel_name)
    worksheet = workbook.add_worksheet()
    with open(path_to_csv, "rt", encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delimiter)
        for r, row in enumerate(reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)
    workbook.close()


def sort_projects_data_per_dictrict(projects_data, subdistricts=False):
    # if subdistricts, will work slightly different
    if subdistricts:
        first_project_dict = next(
            iter(next(iter(projects_data.values())).values()))[0]
    else:
        first_project_dict = next(iter(projects_data.values()))[0]
    if "score" in first_project_dict:
        score_field = "score"
    else:
        score_field = "votes"
    if subdistricts:
        return {
            district: {
                subdistrict: sorted(
                    subdistrict_data, key=lambda d: d[score_field], reverse=True
                )
                for subdistrict, subdistrict_data in subdistrict.items()
            }
            for district, subdistrict in projects_data.items()
        }
    return {
        district: sorted(
            projects_list, key=lambda d: d[score_field], reverse=True)
        for district, projects_list in projects_data.items()
    }


def get_selected_output_files(country, city, year, files):
    file_beginning = f"{country}_{city}_{str(year)}"
    output = settings.output_path.replace("\\", "/")
    if files == "pbs":
        output += "/*.pb"
    elif files == "jsons":
        output += "/jsons/*.json"
    names = [os.path.basename(x) for x in glob.glob(output)]
    names = [name for name in names if name.startswith(file_beginning)]
    if files == "pbs":
        return [os.path.join(settings.output_path, name) for name in names]
    if files == "jsons":
        return [os.path.join(settings.output_path, "jsons", name) for name in names]


def largest_remainder_method(numbers):
    numbers = np.array(numbers)

    # Normalize the numbers so they sum to 1
    norm_numbers = numbers / numbers.sum()

    # Multiply the normalized numbers by the target total (100 in your case) and floor the result
    quotients = np.floor(norm_numbers * 100)

    # Calculate the remainders
    remainders = norm_numbers * 100 - quotients

    # Calculate how many points we still have to distribute
    points_left = 100 - quotients.sum()

    # While we still have points left to distribute
    while points_left > 0:
        # Find the index of the maximum remainder
        max_remainder_index = np.argmax(remainders)

        # Add a point to the number with the maximum remainder
        quotients[max_remainder_index] += 1

        # This number's remainder is now 0
        remainders[max_remainder_index] = 0

        # We've distributed a point
        points_left -= 1

    quotients = quotients.astype(int)
    return list(quotients)


def get_str_with_sep_from(number):
    return f'{number:,d}'.replace(',', ' ')


def sort_projects_by_results(projects):
    first_project_dict = next(iter(projects.values()))
    if "score" in first_project_dict:
        score_field = "score"
    else:
        score_field = "votes"
    projects = dict(
        sorted(
            projects.items(),
            key=lambda x: int(x[1][score_field]),
            reverse=True,
        )
    )
    return projects
