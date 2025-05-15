from copy import deepcopy
from dataclasses import dataclass

from pabulib.checker import flds

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class CreateMetaSections(BaseConfig):
    budgets: dict
    metadata: dict

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
            elif subdistrict.lower() in ("citywide"):
                return self.budgets[district][0]
            else:
                self.logger.critical(f"Gdynia: Not known subdistrict: {subdistrict}!")
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
            try:
                budget = self.budgets[district]
            except KeyError:
                budget = self.budgets[district_upper]
            self.handle_file(district, district_upper, budget)

    def handle_file(self, district, district_upper, budget, subdistrict=None):
        if district_upper.startswith("CITYWIDE"):
            path_to_file = utils.get_path_to_file(self.unit_file_name)
            district = "unit"
        else:
            path_to_file = utils.get_path_to_file(self.unit_file_name, district_upper)
        metadata = self.create_metadata(path_to_file, district, budget, subdistrict)
        metadata = {
            key: metadata[key] for key in flds.META_FIELDS_ORDER if key in metadata
        }
        metadata_txt = "META\nkey;value\n"
        for key, value in metadata.items():
            metadata_txt += f"{key};{value}\n"
        utils.prepend_line_at_the_beggining_of_file(metadata_txt, path_to_file)

    def create_subunit_value(self, metadata, district, subdistrict):
        if metadata.get("subdistrict_sizes"):
            metadata.pop("subdistrict_sizes")
            return f"{district} | {subdistrict}\n"
        return subdistrict

    def create_metadata(self, path_to_file, district, budget, subdistrict):
        temp_meta = deepcopy(self.metadata)
        if district == "unit":
            description = f"Municipal PB in {self.unit.title()}"
            subunit = ""
            district_txt = ""
            dict_to_update = temp_meta.pop("unit", None)
            temp_meta.pop("district", None)

        else:
            if self.subdistricts_mapping:
                district = self.subdistricts_mapping[district]
            unit = self.unit.title()
            district_title = district.title()
            if temp_meta.get("district") and temp_meta["district"].get("description"):
                description = temp_meta["district"].pop("description")
            elif self.subdistricts_mapping or subdistrict:
                if subdistrict in ("small", "large"):
                    subdistrict_txt = subdistrict
                else:
                    subdistrict_txt = subdistrict.title()
                description = (
                    f"Local PB in {unit}, " f"{district_title} | {subdistrict_txt}"
                )
            else:
                description = f"District PB in {unit}, {district_title}"
            if not subdistrict:
                subdistrict_txt = district.title()
            district_txt = district_title

            subunit = self.create_subunit_value(
                temp_meta, district_title, subdistrict_txt
            )

            dict_to_update = temp_meta.pop("district", None)
            temp_meta.pop("unit", None)

        if dict_to_update:
            temp_meta.update(dict_to_update)
        num_projects, num_votes = utils.count_projects_and_votes(path_to_file)

        metadata = {
            "description": description,
            "country": self.country,
            "unit": self.unit,
            "instance": self.instance,
            "num_projects": num_projects,
            "num_votes": num_votes,
            "budget": budget,
        }
        if district_txt:
            metadata["district"] = district_txt
        if subunit:
            metadata["subunit"] = subunit.strip("\n")
        for key, value in temp_meta.items():
            if key == "comment":
                comments = [f"#{idx}: {com}" for idx, com in enumerate(value, 1)]
                value = " ".join(comments)
            metadata[key] = value

        # ADD fully_funded flag
        all_projects = self.get_json_file("projects_data_per_district")
        if district == "unit":
            district = "CITYWIDE"
        if self.subdistricts:
            projects = all_projects[district][subdistrict]
            # raise RuntimeError("NEEDS TO BE CHECKED WITH SUBDISTRICTS!!!")
        else:
            try:
                projects = all_projects[district.upper()]
            except KeyError:
                projects = all_projects[district.title()]
        fully_funded = utils.check_if_fully_funded(budget, projects)
        if fully_funded:
            metadata["fully_funded"] = 1

        return metadata
