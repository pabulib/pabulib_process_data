from dataclasses import dataclass
from copy import deepcopy

from process_data.base_config import BaseConfig

import helpers.utilities as utils


@dataclass
class CreateMetaSections(BaseConfig):
    budgets: dict()
    metadata: dict()
    subdistricts: bool = False

    def __post_init__(self):
        self.set_up_iterator()

        if self.metadata.get("subdistricts_mapping"):
            self.subdistricts_mapping = self.get_json_file(
                "subdistrict_district_mapping"
            )
            self.metadata.pop("subdistricts_mapping")
        else:
            self.subdistricts_mapping = None
        return super().__post_init__()

    def set_up_iterator(self):
        if self.subdistricts:
            iterator = "district_projects_mapping"
        else:
            iterator = "district_upper_district_mapping"
        self.iterator = self.get_json_file(iterator)

    def add_metadata(self):
        self.logger.info("Creating METADATA sections...")
        if self.subdistricts:
            self.iterate_through_subdistricts()
        else:
            self.iterate_through_districts()
        self.logger.info("METADATA sections created")

    def get_subdistrict_budget(self, district, subdistrict):
        if self.unit == "Gdynia":
            if subdistrict == "large":
                return self.budgets[district][0]
            elif subdistrict == "small":
                return self.budgets[district][1]
            elif subdistrict.lower() in ("citywide", "ogolnomiejski"):
                return self.budgets[district][0]
            else:
                self.logger.critical(
                    f"Gdynia: Not known subdistrict: {subdistrict}!")
        return self.budgets[district][subdistrict]

    def iterate_through_subdistricts(self):
        for district, projects in self.iterator.items():
            for subdistrict, _ in projects.items():
                budget = self.get_subdistrict_budget(district, subdistrict)
                district_upper = utils.change_district_into_name(district)
                district_upper = utils.create_district_subdistrict_upper(
                    district_upper, subdistrict
                )
                self.handle_file(district, district_upper, budget, subdistrict)

    def iterate_through_districts(self):
        for district_upper, district in self.iterator.items():
            budget = self.budgets[district]
            self.handle_file(district, district_upper, budget)

    def handle_file(self, district, district_upper, budget, subdistrict=None):
        if district_upper.startswith(("OGOLNO", "CITYWIDE")):
            path_to_file = utils.get_path_to_file(self.unit_file_name)
            district = "unit"
        else:
            path_to_file = utils.get_path_to_file(
                self.unit_file_name, district_upper)
        metadata = self.create_metadata(
            path_to_file, district, budget, subdistrict)
        utils.prepend_line_at_the_beggining_of_file(metadata, path_to_file)

    def create_subunit_value(self, metadata, district, subdistrict):
        if metadata.get("subdistrict_sizes"):
            metadata.pop("subdistrict_sizes")
            return f"subunit;{district} | {subdistrict}\n"
        return f"subunit;{subdistrict}\n"

    def create_metadata(self, path_to_file, district, budget, subdistrict):
        temp_meta = deepcopy(self.metadata)
        if district == "unit":
            description = f"Municipal PB in {self.unit.title()}"
            subunit = ""
            district_txt = ""
            dict_to_update = temp_meta.pop("unit")
            temp_meta.pop("district")

        else:
            if not subdistrict:
                subdistrict = district
            if self.subdistricts_mapping:
                district = self.subdistricts_mapping[district]
            if temp_meta.get('district') and temp_meta['district'].get('description'):
                description = temp_meta['district'].pop('description')
            elif self.subdistricts_mapping or subdistrict:
                description = (
                    f"Local PB in {self.unit.title()}, "
                    f"{district} | {subdistrict}"
                )
            else:
                description = f"District PB in {self.unit.title()}, {district}"
            district_txt = f"district;{district}\n"

            subunit = self.create_subunit_value(
                temp_meta, district, subdistrict)

            dict_to_update = temp_meta.pop("district")
            temp_meta.pop("unit")

        temp_meta.update(dict_to_update)
        num_projects, num_votes = utils.count_projects_and_votes(path_to_file)

        metadata = (
            "META\n"
            "key;value\n"
            f"description;{description}\n"
            f"country;{self.country}\n"
            f"unit;{self.unit}\n"
            f"{subunit}"
            f"instance;{self.instance}\n"
            f"{district_txt}"
            f"num_projects;{num_projects}\n"
            f"num_votes;{num_votes}\n"
            f"budget;{budget}\n"
        )
        for key, value in temp_meta.items():
            metadata += f"{key};{value}\n"
        return metadata
