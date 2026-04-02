import collections
import itertools
import json
import re
from dataclasses import dataclass

import pandas as pd

import helpers.utilities as utils
from helpers.mappings import wroclaw_mapping
from process_data.base_config import BaseConfig
from process_data.models import ProjectItem


@dataclass
class GetProjects(BaseConfig):
    district_projects: bool = True
    excel_filename: str = None
    votes_filename: str = None

    def __post_init__(self):
        self.logger = utils.create_logger()
        self.initialize_mapping_dicts()
        return super().__post_init__()

    def initialize_mapping_dicts(self):
        self.projects_data_per_district = collections.defaultdict(list)
        self.district_projects_mapping = collections.defaultdict(list)
        self.project_district_mapping = dict()

    def iterate_through_projects(self, project_list):
        for project in project_list:
            self.get_project_data(project)

    def get_binary_status(self, status_txt):
        status_txt = status_txt.lower()
        if status_txt == "projectselected":
            return 1
        elif status_txt == "projectnotselected":
            return 0
        else:
            self.logger.error("I cannot parse project status: {status_txt}")

    def get_neighborhood_from_project_url(self, soup):
        cols = soup.find_all("div", class_="col-sm-3")
        for col in cols:
            if re.search(r"Osiedl[ea]", col.span.text):
                neighborhood = col.find_all(text=True)[2].strip()
                return neighborhood
        cols = soup.find_all("p", class_="txtMapDesc")
        for col in cols:
            if re.search(r"Osiedl[ea]", col.span.text):
                neighborhood = col.find_all(text=True)[2].strip()
                return neighborhood
        self.logger.info("I did not find a neighborhood! url: {url}")

    def handle_categories(self, labels):
        categories_to_skip = [
            "Szczepin",
            "Przedmieście Oławskie",
            "Borek",
            "Zacisze-Zalesie-Szczytniki",
        ]
        categories = []
        for label in labels:
            category_pl = label.text.strip()
            if category_pl:
                if category_pl in categories_to_skip:
                    continue
                try:
                    category_eng = wroclaw_mapping[category_pl]
                except KeyError:
                    self.logger.error(f"I didn't find category! {category_pl}")
                    continue
                categories.append(category_eng)
        categories = ",".join(categories)
        return categories

    def handle_categories_excel(self, category_pl):
        categories = []
        for value in str(category_pl).split(","):
            category_pl = value.strip()
            if not category_pl:
                continue
            try:
                category_eng = wroclaw_mapping[category_pl]
                categories.append(category_eng)
            except KeyError:
                self.logger.error(f"I didn't find category! {category_pl}")
        return ",".join(categories)

    def get_excel_column_index(self, col_names_indexes, *column_names):
        for column_name in column_names:
            if column_name in col_names_indexes:
                return column_name
        raise KeyError(f"Cannot find any of columns: {column_names}")

    def get_map_geojson(self, soup):
        script_pattern = re.compile(r"geojsonFeature = (\{.*?\});", re.DOTALL)
        script_tag = soup.find("script", text=script_pattern)

        if script_tag:
            match = script_pattern.search(script_tag.string)
            if match:
                geojson_data = match.group(1)
                geojson_dict = json.loads(geojson_data)
                return geojson_dict

    def get_coordinates_from_project_url(self, item, soup):
        geojson_dict = self.get_map_geojson(soup)
        if geojson_dict:

            latitudes = []
            longitudes = []

            for element in geojson_dict["features"]:
                geometry = element["geometry"]
                if geometry["type"] == "Point":
                    coordinates = geometry["coordinates"]
                    latitudes += [coordinates[0]]
                    longitudes += [coordinates[1]]
            if latitudes:
                item.longitude = sum(longitudes) / len(longitudes)
                item.latitude = sum(latitudes) / len(latitudes)

        return item

    def get_data_from_project_url(self, item):
        soup = utils.get_soup(item.project_url)
        item.district = self.get_neighborhood_from_project_url(soup)
        votes = soup.find("div", class_="boxProjectVotesCount").text
        votes = votes.replace("Głosów:", "")
        item.add_votes(votes)
        item = self.get_coordinates_from_project_url(item, soup)
        return item

    def get_project_data(self, project):
        try:
            status_txt = project["class"][2]
        except IndexError:
            status_txt = project.find("p", class_="txtStatus").text
            if status_txt.strip().lower() in (
                "projekt już realizowany poza wbo",
                "zgłoszony",
            ):
                return
            raise RuntimeError(f"Not known project status: {status_txt}")
        if status_txt == "projectRejected":  # project not approved for voting
            return
        project_no = project.find("p", class_="txtNo").span.text.strip()
        item = ProjectItem(project_no)
        self.logger.info(f"Processing project {project_no}...")
        project_name = project.find("h2", class_="txtTitle").text.strip()
        item.add_name(project_name)
        item.selected = self.get_binary_status(status_txt)
        labels = project.find_all("span", class_="boxLabel")
        item.project_url = project.find("a").get("href")
        project_type = labels[0].text.strip()
        item = self.get_data_from_project_url(item)
        if project_type.lower() == "ponadosiedlowy":
            district = "CITYWIDE"
        elif project_type.lower() == "osiedlowy":
            district = "LOCAL"
        else:
            self.logger.error(
                "district different than Ponadosiedlowy or Osiedlowy: "
                f"{project_type}! url: {item.project_url}"
            )
        item.add_cost(labels[-1].text.strip())
        item.category = self.handle_categories(labels[1:-1])
        self.add_projects_to_mappings(item, district)

    def add_projects_to_mappings(self, item, district):
        self.projects_data_per_district[district].append(vars(item))
        self.district_projects_mapping[district].append(item.project_id)
        self.project_district_mapping[int(item.project_id)] = district

    def create_project_list_url(self, page):
        return (
            "https://www.wroclaw.pl/budzet-obywatelski-wroclaw/"
            f"projekty-{self.instance}/szukaj,id,,name,,type,,"
            f"osiedle,,kategoria,,status,1,kind,,selected,2,strona,{page}"
        )

    def iterate_through_project_list_2022(self):
        for page_no in itertools.count(start=1):
            url = self.create_project_list_url(page_no)
            soup = utils.get_soup(url)
            project_list = soup.find("ul", class_="listProjects").find_all(
                "li", class_="boxProjectHeader"
            )
            if len(project_list) == 0:
                break
            self.logger.info(f"Scraping url {url}...")
            self.iterate_through_projects(project_list)

    def get_projects_votes_from_url(self):
        projects_votes = {}
        url = f"https://www.wroclaw.pl/wbo/wyniki-glosowania-wbo-{self.instance}"
        soup = utils.get_soup(url)
        tables = soup.find_all("div", class_="table-responsive")
        for table in tables:
            table = table.find("tbody")
            rows = table.find_all("tr")
            for row in rows:
                values = row.find_all("td")
                if len(values) > 3:
                    project_id = int(
                        values[1].find("span", class_="numberBox__txt").text.strip()
                    )
                    votes = int(values[3].text.strip())
                    projects_votes[project_id] = votes
        return projects_votes

    def get_projects_votes_from_file(self):
        projects_votes = {}
        path_to_file = utils.get_path_to_file_by_unit(
            self.votes_filename, self.unit, ext="csv"
        )
        votes_df = pd.read_csv(path_to_file, sep=";", encoding="cp1250")
        for project_column in ["Osiedlowy", "Ponadosiedlowy"]:
            counts = (
                votes_df[votes_df[project_column] != 0][project_column]
                .value_counts()
                .to_dict()
            )
            for project_id, votes in counts.items():
                projects_votes[int(project_id)] = int(votes)
        return projects_votes

    def get_data_from_excel(self):
        if self.votes_filename:
            projects_votes = self.get_projects_votes_from_file()
        else:
            projects_votes = self.get_projects_votes_from_url()
        path_to_excel = utils.get_path_to_file_by_unit(self.excel_filename, self.unit)
        df = pd.read_excel(path_to_excel, header=1)
        winners_col = self.get_excel_column_index(
            df.columns, "Projekty wygrane", "Wygrany projekt"
        )
        votes_col = self.get_excel_column_index(
            df.columns,
            "Liczba głosów projektów wygranych",
            "Liczba głosów na wygrane projekty",
        )
        for _, row in df.iterrows():
            name = row["Nazwa projektu"]
            cost = row["Zweryfikowany budżet"]
            if pd.isna(name):
                continue
            if name.startswith("[PROJEKT WYCOFANY") or not cost:
                continue
            project_id = int(row["Numer projektu"])
            item = ProjectItem(project_id)
            item.add_name(name)
            selected = row[winners_col]
            item.selected = 1 if selected in ["wygrany", "tak"] else 0
            item.project_url = f"https://www.wroclaw.pl/wbo/projekty-{self.instance}/projekt,id,{project_id}"
            item.district = row["Nazwa osiedla"]
            item.neighborhood = row["Nazwa osiedla"]
            category_pl = row["Kategoria projektu"]
            item.category = self.handle_categories_excel(category_pl)
            project_type = row["Zasięg projektu"]
            if project_type.lower() == "ponadosiedlowy":
                district = "CITYWIDE"
            elif project_type.lower() == "osiedlowy":
                district = "LOCAL"

            item.add_cost(cost)
            votes_from_excel = row[votes_col]
            try:
                votes_from_url = projects_votes[project_id]
            except KeyError:
                self.logger.info(
                    f"Project `{project_id}` probably was not admitted to the voting process.\n"
                    f"url: https://www.wroclaw.pl/wbo/projekty-{self.instance}/projekt,id,{project_id}"
                )
                continue
            if pd.notna(votes_from_excel):
                votes_from_excel = int(votes_from_excel)
                if votes_from_excel != votes_from_url:
                    raise RuntimeError(
                        "Number of votes is different! Project ID: "
                        f"{project_id}, from excel: {votes_from_excel} "
                        f"vs from url: {votes_from_url}"
                    )

            item.votes = votes_from_url
            self.add_projects_to_mappings(item, district)

    def iterate_through_project_list(self):
        if self.instance == 2022:
            self.iterate_through_project_list_2022()
        elif self.instance > 2022:
            self.get_data_from_excel()

    def start(self):
        self.iterate_through_project_list()
        self.district_upper_district_mapping = {
            "CITYWIDE": "citywide",
            "LOCAL": "local",
        }
        objects = {
            "district_projects_mapping": self.district_projects_mapping,
            "projects_data_per_district": self.projects_data_per_district,
            "project_district_mapping": self.project_district_mapping,
            "district_upper_district_mapping": self.district_upper_district_mapping,
        }
        self.save_mappings_as_jsons(objects)
