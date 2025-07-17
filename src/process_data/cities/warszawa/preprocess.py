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

Utilities used:
- `utils.get_soup` for standard HTML fetching
- `utils.get_soup_requests_with` for detail page parsing
- `utils.create_json_filepath` and `utils.save_dict_as_json` for saving results
"""

import ast
import itertools
import os
import re
from dataclasses import dataclass

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict = None

    def __post_init__(self):
        self.logger = utils.create_logger()
        self.logger.info("Initialized Preprocess class.")
        return super().__post_init__()

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
            soup = utils.get_soup(url)
            projects_table = soup.find("tbody", attrs={"id": "projects-list"})

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
                detail_soup = utils.get_soup_requests_with(full_url)

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
