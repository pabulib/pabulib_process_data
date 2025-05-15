from dataclasses import dataclass

from pabulib.checker import flds

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class CreateProjectsSections(BaseConfig):
    unit_fields: list
    districts_fields: list = None

    def __post_init__(self):
        self.load_json_files()
        self.check_if_districts_fields()
        return super().__post_init__()

    def check_if_districts_fields(self):
        self.districts_fields = self.districts_fields or self.unit_fields

    def load_json_files(self):
        self.district_projects_mapping = self.get_json_file("district_projects_mapping")
        self.project_district_mapping = self.get_json_file("project_district_mapping")
        projects_data_per_district = self.get_json_file("projects_data_per_district")
        self.projects_data_per_district = utils.sort_projects_data_per_dictrict(
            projects_data_per_district, subdistricts=self.subdistricts
        )

    def add_projects_section(self, csv_file, fields):
        csv_file.writerow(["PROJECTS"])
        csv_file.writerow(fields)

    def create_projects_sections(self):
        self.logger.info("Creating PROJECTS sections")

        for district, projects in self.projects_data_per_district.items():
            if self.subdistricts:
                for subdistrict, projects in projects.items():
                    self.unpack_district_projects(district, projects, subdistrict)

            else:
                self.unpack_district_projects(district, projects)

        self.logger.info("PROJECTS sections created")

    def unpack_district_projects(self, district, projects, subdistrict=None):
        if district.upper().startswith("CITYWIDE"):
            file_, csv_file = utils.create_csv_file(self.unit_file_name)
            fields = self.unit_fields
        else:
            district_upper = utils.change_district_into_name(district)
            if self.subdistricts:
                district_upper = utils.create_district_subdistrict_upper(
                    district_upper, subdistrict
                )
            file_, csv_file = utils.create_csv_file(self.unit_file_name, district_upper)
            fields = self.districts_fields

        # sort to be consistent with order in fields.py file
        fields = [field for field in flds.PROJECTS_FIELDS_ORDER if field in fields]

        self.add_projects_section(csv_file, fields)

        for project_dict in projects:
            row = []
            for field in fields:
                if field == "cost":
                    cost = project_dict[field]
                    project_dict[field] = utils.make_cost_printable(cost)
                row.append(project_dict[field])
            csv_file.writerow(row)
        file_.close()
