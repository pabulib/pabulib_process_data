"""
Scrapes project coordinates (latitude and longitude) from the Warsaw participatory budgeting portal
for a given edition year and saves them as a dictionary mapping project IDs to coordinates.

Structure of saved data:
{
    project_id: {"lat": <latitude>, "lng": <longitude>},
    ...
}

Supports both district-level (scope=1) and city-wide (scope=2) projects.
Coordinates are extracted from the detailed project pages using the 'markersMap' input field.

The preprocessor also verifies that official per-project totals match the
anonymized ballot source when that policy is enabled in city settings.

Utilities used:
- a requests session with a browser user agent for portal pages
- `utils.create_json_filepath` and `utils.save_dict_as_json` for saving results
"""

import ast
import collections
import itertools
import os
import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict = None

    def __post_init__(self):
        self.logger = utils.create_logger()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/140.0 Safari/537.36"
                )
            }
        )
        self.logger.info("Initialized Preprocess class.")
        return super().__post_init__()

    @staticmethod
    def normalize_project_id(value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value).strip()

    def validate_project_vote_totals(self):
        if not isinstance(self.preprocess, dict):
            return
        if not self.preprocess.get("require_matching_project_vote_totals"):
            return

        data_dir = self.preprocess["data_dir"]
        projects_path = utils.get_path_to_file_by_unit(
            self.preprocess["projects_excel_filename"],
            self.unit,
            extra_dir=data_dir,
        )
        votes_path = utils.get_path_to_file_by_unit(
            self.preprocess["votes_excel_filename"],
            self.unit,
            extra_dir=data_dir,
        )

        projects_sheet = utils.open_excel_workbook(projects_path)
        project_columns = utils.get_col_names_indexes(projects_sheet)
        project_id_column = project_columns[self.preprocess["project_id_column"]]
        official_votes_column = project_columns[
            self.preprocess["official_votes_column"]
        ]

        official_totals = {}
        for row_number in range(1, projects_sheet.nrows):
            row = projects_sheet.row_values(row_number)
            votes = row[official_votes_column]
            if votes == "":
                continue
            project_id = self.normalize_project_id(row[project_id_column])
            if project_id in official_totals:
                raise RuntimeError(f"Duplicated Warsaw project ID: {project_id}")
            official_totals[project_id] = int(votes)

        votes_sheet = utils.open_excel_workbook(votes_path)
        vote_columns = utils.get_col_names_indexes(votes_sheet)
        validity_column = vote_columns[self.preprocess["validity_column"]]
        ballot_vote_columns = [
            vote_columns[column]
            for column in self.preprocess["ballot_vote_columns"]
        ]
        valid_value = self.preprocess["valid_value"]

        ballot_totals = collections.Counter()
        for row_number in range(1, votes_sheet.nrows):
            row = votes_sheet.row_values(row_number)
            if row[validity_column] != valid_value:
                continue
            for column in ballot_vote_columns:
                votes = row[column]
                if votes == "":
                    continue
                if isinstance(votes, float):
                    project_ids = [self.normalize_project_id(votes)]
                else:
                    project_ids = [
                        self.normalize_project_id(project_id)
                        for project_id in str(votes).split(",")
                        if project_id.strip()
                    ]
                ballot_totals.update(project_ids)

        official_project_ids = set(official_totals)
        ballot_project_ids = set(ballot_totals)
        missing_from_ballots = sorted(
            official_project_ids - ballot_project_ids, key=int
        )
        missing_from_projects = sorted(
            ballot_project_ids - official_project_ids, key=int
        )
        mismatches = [
            (project_id, official_totals[project_id], ballot_totals[project_id])
            for project_id in sorted(
                official_project_ids & ballot_project_ids, key=int
            )
            if official_totals[project_id] != ballot_totals[project_id]
        ]

        if missing_from_ballots or missing_from_projects or mismatches:
            raise RuntimeError(
                "Warsaw official/ballot vote mismatch: "
                f"official_only={missing_from_ballots[:20]}, "
                f"ballot_only={missing_from_projects[:20]}, "
                f"totals={mismatches[:20]}"
            )

        self.logger.info(
            "Warsaw official project totals match anonymized ballots: "
            f"{len(official_totals)} projects, {sum(official_totals.values())} votes."
        )

    def get_soup(self, url):
        response = self.session.get(url, timeout=60)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    def create_project_list_url(self, page_no):
        url = (
            "https://bo.um.warszawa.pl/projects?"
            f"filter[edition_year][]={self.instance}"
            "&filter[per_page]=120"
            f"&page={page_no}"
        )
        self.logger.debug(f"Generated URL: {url}")
        return url

    def get_coordinates(self, soup):
        try:
            map_str = soup.find("input", attrs={"name": "markersMap"}).get("value")
            map_dict = ast.literal_eval(map_str)
            latitudes = [float(coords["lat"]) for coords in map_dict.values()]
            longitudes = [float(coords["lng"]) for coords in map_dict.values()]
            if latitudes and longitudes:
                lat = sum(latitudes) / len(latitudes)
                lon = sum(longitudes) / len(longitudes)
                return lon, lat
        except Exception as e:
            self.logger.warning(f"Failed to extract coordinates: {e}")
        return "", ""

    def scrape_projects_coordinates(self):
        self.logger.info(f"Starting coordinate scraping for year: {self.instance}")
        coordinates_dict = {}

        for page_no in itertools.count(start=1):
            url = self.create_project_list_url(page_no)
            self.logger.info(f"Fetching URL: {url}")
            soup = self.get_soup(url)
            projects_table = soup.find("tbody", attrs={"id": "projects-list"})

            if projects_table is None:
                raise RuntimeError(f"Could not find Warsaw projects table at {url}")

            rows = projects_table.find_all("tr", recursive=False)

            rows = [r for r in rows if r.get_text(strip=True)]

            if len(rows) == 1 and "Brak wyników" in rows[0].get_text(strip=True):
                self.logger.info(f"No results found on page {page_no} — stopping.")
                break

            # only for testing
            # if page_no > 2:
            #     self.logger.warning("Page limit reached (debug limit = 2).")
            #     break

            for project in projects_table.find_all("tr"):
                href_tag = project.find("a", class_="card__link")
                if not href_tag or not href_tag.get("href"):
                    continue

                href = href_tag.get("href")
                full_url = f"https://bo.um.warszawa.pl{href}"
                self.logger.debug(f"Scraping project page: {full_url}")
                detail_soup = self.get_soup(full_url)

                scope_and_number = project.find("div", class_="scope-and-number")
                if scope_and_number:
                    raw_text = scope_and_number.text.strip()
                    match = re.search(r"(\d+)$", raw_text)
                    if match:
                        project_id = int(match.group(1))
                    else:
                        self.logger.warning(
                            f"Could not extract project ID with regex from: '{raw_text}'"
                        )
                        continue
                else:
                    self.logger.warning(
                        "No 'scope-and-number' div found in project row."
                    )
                    continue

                lon, lat = self.get_coordinates(detail_soup)
                if lon and lat:
                    coordinates_dict[project_id] = {"lat": lat, "lng": lon}
                else:
                    self.logger.debug(f"No coordinates for project {project_id}.")

                # only for testing
                # break

        self.logger.info(f"Collected {len(coordinates_dict)} project coordinates.")
        return coordinates_dict

    def start(self):
        self.validate_project_vote_totals()
        obj_name = "project_coordinates"
        json_filepath = utils.create_json_filepath(
            self.country, self.unit, self.instance, obj_name
        )

        if os.path.exists(json_filepath):
            self.logger.info(
                f"File already exists: {os.path.basename(json_filepath)} — skipping scraping."
            )
            return

        coordinates_dict = self.scrape_projects_coordinates()
        # Save to JSON
        utils.save_dict_as_json(coordinates_dict, json_filepath)
        self.logger.info(f"Saved coordinates to {os.path.basename(json_filepath)}")
