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
- `utils.create_json_file_name` and `utils.save_dict_as_json` for saving results
"""

import ast
import itertools
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

    def create_project_list_url(self, page_no, scope):
        url = (
            "https://bo.um.warszawa.pl/projects?utf8=%E2%9C%93&filter%5B"
            "search_text%5D=&filter%5Bper_page%5D=120&filter%5Bedition_"
            "year%5D%5B%5D=&filter%5Bedition_year%5D%5B%5D="
            f"{self.instance}&filter%5Bscope_type%5D%5B%5D=&filter%5B"
            f"scope_type%5D%5B%5D={scope}&filter%5Bscope_id%5D%5B%5D="
            "&filter%5Bcategory%5D%5B%5D=&filter%5Bpotential_recipient%5"
            "D%5B%5D=&filter%5Bstate%5D%5B%5D=&filter%5Bstate%5D%5B%5D="
            "selected&filter%5Bstate%5D%5B%5D=not_selected&"
            f"page={page_no}"
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

        for scope in [1, 2]:  # 1 = district, 2 = unit-wide
            scope_name = "district" if scope == 1 else "unit-wide"
            self.logger.info(f"Processing scope: {scope_name}")
            for page_no in itertools.count(start=1):
                url = self.create_project_list_url(page_no, scope)
                self.logger.info(f"Fetching URL: {url}")
                soup = utils.get_soup(url)
                projects_table = soup.find("tbody", attrs={"id": "projects-list"})

                if not projects_table:
                    self.logger.info("No project table found — likely no more pages.")
                    break

                rows = projects_table.find_all("tr")
                if not rows:
                    self.logger.info("Project table is empty — end of data.")
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
        coordinates_dict = self.scrape_projects_coordinates()
        # Save to JSON
        obj_name = "project_coordinates"
        json_file_name = utils.create_json_file_name(
            self.country, self.unit, self.instance, obj_name
        )
        utils.save_dict_as_json(coordinates_dict, json_file_name)
        self.logger.info(f"Saved coordinates to {json_file_name}")
        raise RuntimeError("Process complete (intentional)")
