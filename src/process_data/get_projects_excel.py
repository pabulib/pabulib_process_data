import collections
from dataclasses import dataclass

import helpers.utilities as utils
from helpers.mappings import category_mapping, target_mapping
from process_data.base_config import BaseConfig
from process_data.models import ProjectItem


@dataclass(kw_only=True)
class GetProjects(BaseConfig):
    excel_filename: str
    columns_mapping: dict
    data_dir: str = None
    excel_ext: str = "xlsx"
    only_score_column: bool = False

    def __post_init__(self):
        self.selected_projects = False
        self.initialize_mapping_dicts()
        return super().__post_init__()

    def handle_columns_indexes(self):
        self.col_names_indexes = utils.get_col_names_indexes(self.sheet)
        # REQUIRED COLUMNS
        self.col = {
            "project_id": self.col_names_indexes[self.columns_mapping["project_id"]],
            "name": self.col_names_indexes[self.columns_mapping["name"]],
            "cost": self.col_names_indexes[self.columns_mapping["cost"]],
            "votes": self.col_names_indexes[self.columns_mapping["votes"]],
            # "selected": self.col_names_indexes[self.columns_mapping["selected"]],
        }
        # OPTIONAL COLUMNS
        for col, value in self.columns_mapping.items():
            if (col not in self.col) and (not isinstance(value, dict)):
                self.col[col] = self.col_names_indexes[value]

    def prepare_excel_sheet(self):
        path_to_excel = utils.get_path_to_file_by_unit(
            self.excel_filename, self.unit, extra_dir=self.data_dir, ext=self.excel_ext
        )
        self.sheet = utils.open_excel_workbook(path_to_excel)

    def map_categories(self, category_pl):
        category_pl = category_pl.lower()
        try:
            category = category_mapping[category_pl]
            return category
        except KeyError:
            raise RuntimeError(f"Cannot translate category: {category_pl}")

    def iterate_through_projects(self):
        for col_idx in range(1, self.sheet.nrows):
            row_values = self.sheet.row_values(col_idx)
            project_id = row_values[self.col["project_id"]]
            if isinstance(project_id, str):
                project_id = project_id.strip()
            elif isinstance(project_id, float):
                project_id = str(int(project_id))
            votes = row_values[self.col["votes"]]
            if project_id in ("", "NULL") or votes == "":
                # Project not allowed to vote
                continue
            item = ProjectItem()
            item.add_project_id(project_id)

            if int(votes) == 0:
                # check it and pass or continue
                # raise RuntimeError(f"Project: {item.project_id} has 0 votes!")
                continue

            name = row_values[self.col["name"]]
            item.add_name(name)

            if self.only_score_column:
                item.add_score(votes)

            else:
                item.add_votes(votes)
            if self.col.get("score"):
                item.add_score(row_values[self.col["score"]])

            if self.col.get("selected"):
                selected = row_values[self.col["selected"]]
                item.add_selected(selected)

            district = row_values[self.col["district"]].strip()
            if district.lower().startswith("ogólnomi"):
                district = "CITYWIDE"
                if self.unit == "Poznań":
                    district = "_CITYWIDE"
            item.neighborhood = district
            if self.unit == "Kraków":
                district = self.check_if_citywide_krakow(district, project_id)
            item.district = district
            if self.col.get("category"):
                category_pl = row_values[self.col["category"]]
                item.category = self.map_categories(category_pl)
            elif self.unit == "Warszawa":
                item.category = self.get_mappings_warszawa("categories", row_values)
                if self.instance < 2026:
                    item.target = self.get_mappings_warszawa("targets", row_values)
            cost = row_values[self.col["cost"]]
            item.add_cost(cost)
            if self.subdistricts:
                item.add_subdistrict(row_values[self.col["subdistrict"]])
            self.add_projects_to_mappings(item)

    def add_projects_to_mappings(self, item):
        district = item.district
        if self.subdistricts:
            subdistrict = item.subdistrict
            if not self.projects_data_per_district.get(district):
                self.projects_data_per_district[district] = collections.defaultdict(
                    list
                )
            self.projects_data_per_district[district][subdistrict].append(vars(item))
            if not self.district_projects_mapping.get(district):
                self.district_projects_mapping[district] = collections.defaultdict(list)
            self.district_projects_mapping[district][subdistrict].append(
                item.project_id
            )
            self.project_subdistrict_mapping[item.project_id] = subdistrict
        else:
            self.projects_data_per_district[district].append(vars(item))
            self.district_projects_mapping[district].append(item.project_id)

        self.project_district_mapping[item.project_id] = district

    def initialize_mapping_dicts(self):
        self.projects_data_per_district = collections.defaultdict(list)
        self.district_projects_mapping = collections.defaultdict(list)
        self.project_district_mapping = dict()
        if self.subdistricts:
            self.project_subdistrict_mapping = dict()

    def create_district_upper_mapping(self):
        self.district_upper_district_mapping = {"CITYWIDE": "citywide"}
        for district in self.district_projects_mapping.keys():
            district_upper = utils.change_district_into_name(district)
            self.district_upper_district_mapping[district_upper] = district

    def check_if_citywide_krakow(self, district, project_id):
        project_type = project_id.split("BO.")[1]
        if project_type.startswith("OM"):
            district = "CITYWIDE"
        return district

    def get_mappings_warszawa(self, mapping_type, row_values):
        if mapping_type == "categories":
            mapping = category_mapping
        elif mapping_type == "targets":
            mapping = target_mapping

        mappings = []
        for cat_pl, cat_eng in mapping.items():

            col_index = self.col_names_indexes.get(cat_pl)
            if col_index:
                if row_values[col_index] == "TAK":
                    mappings.append(cat_eng)
        if mappings and mappings[0]:
            return ",".join(mappings)

    def post_process(self):
        if self.unit == "Warszawa":
            # Add project coordinates from JSON (scrpaed in preprocess)
            filename = "project_coordinates"
            filepath = utils.create_json_filepath(
                self.country, self.unit, self.instance, filename
            )
            coordinates_dict = utils.load_json_obj(filepath)

            # Inject lat/lng into project dictionaries
            for _, projects in self.projects_data_per_district.items():
                for project in projects:
                    project_id = str(project.get("project_id"))
                    coords = coordinates_dict.get(project_id)
                    if coords:
                        project["latitude"] = coords.get("lat")
                        project["longitude"] = coords.get("lng")

    def start(self):
        self.prepare_excel_sheet()
        self.handle_columns_indexes()
        self.iterate_through_projects()
        self.create_district_upper_mapping()
        self.post_process()
        objects = {
            "district_projects_mapping": self.district_projects_mapping,
            "projects_data_per_district": self.projects_data_per_district,
            "project_district_mapping": self.project_district_mapping,
            "district_upper_district_mapping": self.district_upper_district_mapping,
        }
        if self.subdistricts:
            objects["project_subdistrict_mapping"] = self.project_subdistrict_mapping
        self.save_mappings_as_jsons(objects)
