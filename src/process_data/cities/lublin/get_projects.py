import collections
import os
import re
from dataclasses import dataclass
from dataclasses import field

import helpers.utilities as utils
from process_data.base_config import BaseConfig
from process_data.cities.lublin.postprocess import register_lublin_postprocess
from process_data.cities.lublin.projects_costs import get_projects_costs

OFFICIAL_SELECTED_PROJECTS_2020 = {
    "D-23", "D-24", "D-15", "D-117", "D-41", "D-107", "D-101", "D-66",
    "D-38", "D-102", "D-97", "D-108", "D-7", "D-26", "D-99", "D-103",
    "D-6", "D-54", "D-39", "D-72", "D-62", "D-36", "D-53", "D-82",
    "D-10", "D-74", "D-92", "O-5", "O-76", "O-79", "O-42", "O-45",
    "O-60", "O-39", "O-78", "O-15", "O-1", "O-38", "O-8", "O-67",
}

OFFICIAL_SELECTED_COST_OVERRIDES_2020 = {
    "D-12": 210000,
    "D-15": 300000,
    "D-26": 300000,
    "D-38": 300000,
    "D-45": 200000,
    "D-53": 300000,
    "D-70": 36000,
    "D-75": 300000,
    "D-82": 250000,
    "D-86": 241000,
    "D-92": 300000,
    "D-103": 140000,
    "D-117": 300000,
    "D-120": 140600,
    "D-128": 100000,
    "D-129": 160000,
    "O-10": 50000,
    "O-47": 23600,
    "O-56": 100000,
    "O-58": 20000,
    "O-67": 1187831,
}

OFFICIAL_SELECTED_LOCAL_DISTRICTS_2020 = {
    "D-23": "Czuby Południowe",
    "D-24": "Czuby Północne",
    "D-15": "Ponikwoda",
    "D-117": "Rury",
    "D-41": "Czechów Północny",
    "D-107": "Zemborzyce",
    "D-101": "Czechów Południowy",
    "D-66": "Kalinowszczyzna",
    "D-38": "Sławin",
    "D-102": "Felin",
    "D-97": "Węglin Południowy",
    "D-108": "Bronowice",
    "D-7": "Węglin Północny",
    "D-26": "Konstantynów",
    "D-99": "Stare Miasto",
    "D-103": "Wrotków",
    "D-6": "Kośminek",
    "D-54": "Dziesiąta",
    "D-39": "Szerokie",
    "D-72": "Wieniawa",
    "D-62": "Abramowice",
    "D-36": "Tatary",
    "D-53": "Śródmieście",
    "D-82": "Za Cukrownią",
    "D-10": "Głusk",
    "D-74": "Sławinek",
    "D-92": "Hajdów-Zadębie",
}

LOCAL_FALLBACK_DISTRICTS_2020 = {
    "D-16": "Czuby Południowe",
    "D-44": "Czechów Północny",
    "D-50": "Czuby Południowe",
    "D-79": "Czuby Północne",
    "D-120": "Czechów Południowy",
    "D-127": "Czechów Północny",
    "D-128": "Kalinowszczyzna",
    "D-129": "Bronowice",
}

CITYWIDE_HARD_UNDER_300K_2020 = {"O-8", "O-11", "O-71", "O-72"}

DISTRICT_NAMES_2020 = sorted(
    {
        "Abramowice",
        "Bronowice",
        "Czechów Południowy",
        "Czechów Północny",
        "Czuby Południowe",
        "Czuby Północne",
        "Dziesiąta",
        "Felin",
        "Głusk",
        "Hajdów-Zadębie",
        "Kalinowszczyzna",
        "Konstantynów",
        "Kośminek",
        "Ponikwoda",
        "Rury",
        "Stare Miasto",
        "Szerokie",
        "Sławin",
        "Sławinek",
        "Tatary",
        "Wieniawa",
        "Wrotków",
        "Węglin Południowy",
        "Węglin Północny",
        "Za Cukrownią",
        "Zemborzyce",
        "Śródmieście",
    },
    key=len,
    reverse=True,
)


@dataclass
class GetProjects(BaseConfig):
    projects_excel: str
    data_dir: str = ""
    csv_settings: dict = field(default_factory=lambda: {})

    def __post_init__(self):
        self.logger = utils.create_logger()
        self.initialize_mapping_dicts()
        self.path_to_excel = utils.get_path_to_file_by_unit(
            self.projects_excel, self.unit, extra_dir=self.data_dir
        )
        return super().__post_init__()

    def initialize_mapping_dicts(self):
        self.projects_data_per_district = collections.defaultdict(list)
        self.district_projects_mapping = collections.defaultdict(list)
        self.projects_votes = dict()
        self.project_id_name_mapping = dict()
        self.project_district_mapping = dict()
        self.project_ballot_districts = collections.defaultdict(collections.Counter)
        self.prefix_district_mapping = self.get_prefix_district_mapping()

    def get_prefix_district_mapping(self):
        mapping = {}
        for line in get_projects_costs.__globals__["text"].splitlines():
            if not line.startswith("D - "):
                continue
            project_id = re.match(r"(D - \d{1,3})", line).group(1).replace(" ", "")
            rest = re.sub(r"^D - \d{1,3}\s*", "", line)
            for district in DISTRICT_NAMES_2020:
                if rest.startswith(f"{district} ") or rest == district:
                    mapping[project_id] = district
                    break
        return mapping

    def get_sheet_data(self):
        if not os.path.exists(self.path_to_excel):
            csv_path = self.path_to_excel.replace(".xlsx", ".csv")
            utils.convert_csv_to_xl(
                csv_path,
                delimiter=self.csv_settings.get("delimiter", ","),
                encoding=self.csv_settings.get("encoding", "utf-8"),
                excel_name=self.path_to_excel,
            )
        sheet = utils.open_excel_workbook(self.path_to_excel)
        data = [sheet.row_values(i) for i in range(sheet.nrows)][1:]
        self.col_names_indexes = utils.get_col_names_indexes(sheet)
        return data

    def iterate_through_rows(self, data):
        for row_data in data:
            # district = row_data[self.col_names_indexes["Dzielnica"]]
            project_id = row_data[self.col_names_indexes["Nr projektu"]]
            project_id = project_id.replace(" ", "")
            project_name = row_data[self.col_names_indexes["Tytuł projektu"]]

            self.projects_votes[project_id] = self.projects_votes.get(
                project_id, 0) + 1

            self.project_id_name_mapping[project_id] = project_name
            if project_id.startswith("D-"):
                district = row_data[self.col_names_indexes["Dzielnica"]]
                self.project_ballot_districts[project_id][district] += 1

    def get_project_cost(self, project_id, projects_costs):
        return OFFICIAL_SELECTED_COST_OVERRIDES_2020.get(
            project_id, projects_costs[project_id]
        )

    def get_citywide_pool(self, project_id, cost):
        if project_id in CITYWIDE_HARD_UNDER_300K_2020 or cost > 300000:
            return "CITYWIDE_HARD"
        return "CITYWIDE_SOFT"

    def get_local_district(self, project_id):
        if project_id in OFFICIAL_SELECTED_LOCAL_DISTRICTS_2020:
            return OFFICIAL_SELECTED_LOCAL_DISTRICTS_2020[project_id]
        if project_id in self.prefix_district_mapping:
            return self.prefix_district_mapping[project_id]
        if project_id in LOCAL_FALLBACK_DISTRICTS_2020:
            return LOCAL_FALLBACK_DISTRICTS_2020[project_id]
        if self.project_ballot_districts.get(project_id):
            return self.project_ballot_districts[project_id].most_common(1)[0][0]
        raise RuntimeError(f"Cannot determine district for project {project_id}")

    def iterate_through_projects(self, projects_costs):
        for project_id, votes in self.projects_votes.items():
            if project_id.startswith("O"):
                cost = self.get_project_cost(project_id, projects_costs)
                district = self.get_citywide_pool(project_id, cost)
            elif project_id.startswith("D"):
                district = self.get_local_district(project_id)
                cost = self.get_project_cost(project_id, projects_costs)
            else:
                raise RuntimeError(f"Different distrct! {project_id}")
            self.district_projects_mapping[district].append(project_id)
            project_dict = {
                "project_id": project_id,
                "name": self.project_id_name_mapping[project_id],
                "votes": votes,
                "cost": cost,
                "selected": int(project_id in OFFICIAL_SELECTED_PROJECTS_2020),
            }
            self.projects_data_per_district[district].append(project_dict)
            self.project_district_mapping[project_id] = district

    def create_district_upper_mapping(self):
        self.district_upper_district_mapping = {}
        for district in self.district_projects_mapping.keys():
            district_upper = utils.change_district_into_name(district)
            self.district_upper_district_mapping[district_upper] = district

    def start(self):
        register_lublin_postprocess(
            country=self.country,
            unit=self.unit,
            instance=int(self.instance),
        )
        data = self.get_sheet_data()
        self.iterate_through_rows(data)
        projects_costs = get_projects_costs()
        self.iterate_through_projects(projects_costs)
        self.create_district_upper_mapping()
        objects = {
            "district_projects_mapping": self.district_projects_mapping,
            "projects_data_per_district": self.projects_data_per_district,
            "project_district_mapping": self.project_district_mapping,
            "district_upper_district_mapping": self.district_upper_district_mapping,
        }
        self.save_mappings_as_jsons(objects)
