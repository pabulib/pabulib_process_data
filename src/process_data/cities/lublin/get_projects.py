import collections
from dataclasses import dataclass

import helpers.utilities as utils
from process_data.base_config import BaseConfig
from process_data.cities.lublin.projects_costs import get_projects_costs


@dataclass
class GetProjects(BaseConfig):
    projects_excel: str

    def __post_init__(self):
        self.logger = utils.create_logger()
        self.initialize_mapping_dicts()
        self.path_to_excel = utils.get_path_to_file_by_unit(
            self.projects_excel, self.unit)
        return super().__post_init__()

    def initialize_mapping_dicts(self):
        self.projects_data_per_district = collections.defaultdict(list)
        self.district_projects_mapping = collections.defaultdict(list)
        self.projects_votes = dict()
        self.project_id_name_mapping = dict()
        self.project_district_mapping = dict()

    def get_sheet_data(self):
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

    def iterate_through_projects(self, projects_costs):
        for project_id, votes in self.projects_votes.items():
            if project_id.startswith("O"):
                district = "CITYWIDE"
            elif project_id.startswith("D"):
                district = "LOCAL"
            else:
                raise RuntimeError(f"Different distrct! {project_id}")
            self.district_projects_mapping[district].append(project_id)
            project_dict = {
                "project_id": project_id,
                "name": self.project_id_name_mapping[project_id],
                "votes": votes,
                "cost": projects_costs[project_id]
            }
            self.projects_data_per_district[district].append(project_dict)
            self.project_district_mapping[project_id] = district

    def create_district_upper_mapping(self):
        self.district_upper_district_mapping = {
            "CITYWIDE": "CITYWIDE",
            "LOCAL": "LOCAL"
        }

    def start(self):
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
