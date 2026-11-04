from dataclasses import dataclass

import helpers.utilities as utils
from process_data.base_config import BaseConfig
from process_data.models import ProjectItem


@dataclass(kw_only=True)
class GetProjects(BaseConfig):
    excel_filename: str
    columns_mapping: dict
    data_dir: str = None
    excel_ext: str = "xlsx"

    def __post_init__(self):
        self.projects_data_per_district = {"CITYWIDE": []}
        self.district_projects_mapping = {"CITYWIDE": []}
        self.project_district_mapping = {}
        return super().__post_init__()

    def start(self):
        path_to_excel = utils.get_path_to_file_by_unit(
            self.excel_filename,
            self.unit,
            extra_dir=self.data_dir,
            ext=self.excel_ext,
        )
        sheet = utils.open_excel_workbook(path_to_excel)
        col_names_indexes = utils.get_col_names_indexes(sheet)
        col = {
            key: col_names_indexes[value]
            for key, value in self.columns_mapping.items()
        }

        for row_idx in range(1, sheet.nrows):
            row = sheet.row_values(row_idx)
            project_id = row[col["project_id"]]
            if project_id in ("", "NULL"):
                continue

            item = ProjectItem()
            item.add_project_id(project_id)
            item.add_cost(row[col["cost"]])
            item.add_votes(row[col["votes"]])
            item.add_name(row[col["name"]])
            item.add_selected(row[col["selected"]])
            item.category = row[col["category"]]
            item.latitude = row[col["latitude"]] or ""
            item.longitude = row[col["longitude"]] or ""
            item.district = "CITYWIDE"

            project = vars(item)
            self.projects_data_per_district["CITYWIDE"].append(project)
            self.district_projects_mapping["CITYWIDE"].append(item.project_id)
            self.project_district_mapping[str(item.project_id)] = "CITYWIDE"

        objects = {
            "district_projects_mapping": self.district_projects_mapping,
            "projects_data_per_district": self.projects_data_per_district,
            "project_district_mapping": self.project_district_mapping,
            "district_upper_district_mapping": {"CITYWIDE": "CITYWIDE"},
        }
        self.save_mappings_as_jsons(objects)
