import csv
from dataclasses import dataclass

from pabulib.checker import flds

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class CreateVotesSections(BaseConfig):
    unit_fields: list
    districts_fields: list = None
    subdistricts: bool = False

    def __post_init__(self):
        self.load_json_files()
        self.check_if_districts_fields()
        return super().__post_init__()

    def check_if_districts_fields(self):
        self.districts_fields = self.districts_fields or self.unit_fields

    def load_json_files(self):
        self.votes_data_per_district = self.get_json_file("votes_data_per_district")

    def add_votes_section(self, csv_file, fields):
        csv_file.writerow(["VOTES"])
        csv_file.writerow(fields)

    def create_votes_sections(self):
        self.logger.info("Creating VOTES sections")
        for district, votes in self.votes_data_per_district.items():

            if self.subdistricts:
                # TODO sort votes in subdistricts
                # votes = sorted(votes, key=lambda d: d["voter_id"])

                if isinstance(votes, list):
                    self.unpack_district_votes(district, votes)
                elif isinstance(votes, dict):
                    for subdistrict, votes in votes.items():
                        self.unpack_district_votes(district, votes, subdistrict)
            else:
                votes = sorted(votes, key=lambda d: d["voter_id"])
                self.unpack_district_votes(district, votes)
        self.logger.info("VOTES sections created")

    def unpack_district_votes(self, district, votes, subdistrict=None):
        if district.upper().startswith("CITYWIDE"):
            fields = self.unit_fields
            path_to_file = utils.get_path_to_file(self.unit_file_name)
        else:
            district_upper = utils.change_district_into_name(district)
            if self.subdistricts:
                district_upper = utils.create_district_subdistrict_upper(
                    district_upper, subdistrict
                )
            path_to_file = utils.get_path_to_file(self.unit_file_name, district_upper)
            fields = self.districts_fields

        # sort to be consistent with order in fields.py file
        fields = [field for field in flds.VOTES_FIELDS_ORDER if field in fields]

        with open(path_to_file, "a+", newline="", encoding="utf-8") as file_:
            csv_file = csv.writer(file_, delimiter=";")
            self.add_votes_section(csv_file, fields)
            for voter_dict in votes:
                row = []
                for field in fields:
                    row.append(voter_dict[field])
                csv_file.writerow(row)
            file_.close()
