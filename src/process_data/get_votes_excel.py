import collections
import os
from copy import deepcopy
from dataclasses import dataclass, field

from natsort import natsorted

import helpers.utilities as utils
from process_data.base_config import BaseConfig
from process_data.models import VoterItem


@dataclass
class GetVotesExcel(BaseConfig):
    excel_filename: str
    columns_mapping: dict
    rows_iterator_handler: str
    valid_value: str = ""
    first_row: int = 1
    data_dir: str = None
    voter_id_integer: bool = True
    district_name_mapping: bool = False
    subdistricts: bool = False
    only_valid_votes: bool = False
    csv_settings: dict = field(default_factory=lambda: {})

    def __post_init__(self):
        self.initialize_mapping_dicts()
        self.set_up_rows_iterator_handler()
        self.initialize_unit_reqs()
        return super().__post_init__()

    def initialize_unit_reqs(self):
        if self.unit in ("Kraków", "Warszawa"):
            self.project_district_mapping = self.get_json_file(
                "project_district_mapping"
            )

    def initialize_mapping_dicts(self):
        self.votes_data_per_district = collections.defaultdict(list)
        if self.district_name_mapping:
            self.district_district_name_mapping = self.get_json_file(
                "district_district_name_mapping"
            )

    def set_up_rows_iterator_handler(self):
        handlers_mapping = {
            "one_voter_one_row_no_points": self.handle_one_row_no_points,
            "one_voter_multiple_rows_no_points": self.handle_multiple_rows,
            "one_voter_multiple_rows_with_points": self.handle_multiple_rows,
        }
        self.handler = handlers_mapping[self.rows_iterator_handler]
        if self.handler == self.handle_multiple_rows:
            self.voter_votes = collections.defaultdict(list)
            if self.rows_iterator_handler == "one_voter_multiple_rows_no_points":
                self.no_points = True
            else:
                self.no_points = False

    def handle_csv(self, path_to_excel):
        if self.excel_filename[-4:] == ".csv":
            self.logger.info("Converting CSV into Excel file...")
            delimiter = self.csv_settings.get("delimiter", ",")
            encoding = self.csv_settings.get("encoding", "utf-8")
            path, _, xlsx = path_to_excel.split(".")
            path_to_csv = f"{path}.csv"
            path_to_excel = f"{path}.{xlsx}"
            if os.path.exists(path_to_excel):
                self.logger.info(
                    """There is already existing Excel file, converting
                     stopped. If you want to convert anyway, 
                     please remove xlsx."""
                )
            else:
                utils.convert_csv_to_xl(
                    path_to_csv, delimiter=delimiter, encoding=encoding
                )
                self.logger.info("Converting finished.")
        return path_to_excel

    def open_excel_sheet(self):
        if self.data_dir:
            path_to_excel = utils.get_path_to_file_by_unit(
                self.excel_filename, self.unit, self.data_dir
            )
        else:
            path_to_excel = utils.get_path_to_file_by_unit(
                self.excel_filename, self.unit
            )
        path_to_excel = self.handle_csv(path_to_excel)
        self.sheet = utils.open_excel_workbook(path_to_excel)
        self.handle_columns_indexes()

    def handle_columns_indexes(self):
        col_names_indexes = utils.get_col_names_indexes(self.sheet)
        # REQUIRED COLUMNS
        self.col = {"voter_id": col_names_indexes[self.columns_mapping["voter_id"]]}
        if self.columns_mapping.get("district"):
            self.col["district"] = col_names_indexes[self.columns_mapping["district"]]
        if not self.only_valid_votes:
            # there are sheets with valid votes only
            self.col["if_valid"] = col_names_indexes[self.columns_mapping["if_valid"]]
        # OPTIONAL COLUMNS
        for col, value in self.columns_mapping.items():
            if (col not in self.col) and (not isinstance(value, dict)):
                self.col[col] = col_names_indexes[value]
        if self.handler == self.handle_multiple_rows and not self.no_points:
            self.points_field = col_names_indexes[self.columns_mapping["points"]]
        self.set_bools_for_optional_columns()
        self.handle_row_iterator_columns(col_names_indexes)
        self.handle_subdistrict(col_names_indexes)

    def set_bools_for_optional_columns(self):
        self.get_age = self.col.get("age")
        self.get_sex = self.col.get("sex")
        self.get_voting_method = self.col.get("voting_method")

    def handle_subdistrict(self, col_names_indexes):
        if self.columns_mapping.get("subdistrict"):
            self.col["subdistrict"] = col_names_indexes[
                self.columns_mapping["subdistrict"]
            ]

    def handle_row_iterator_columns(self, col_names_indexes):
        if self.rows_iterator_handler == "one_voter_one_row_no_points":
            votes_columns = self.columns_mapping["votes_columns"]
            self.col["unit_votes"] = col_names_indexes[votes_columns["unit"]]
            # self.col["district_votes"] = col_names_indexes[votes_columns["district"]]
            del votes_columns["unit"]
            self.district_columns = {
                key: col_names_indexes[value] for key, value in votes_columns.items()
            }
            # for subdistrict, district_votes in self.district_columns:
            # district_votes = row[self.col["district_votes"]]
        elif self.handler == self.handle_multiple_rows:
            self.vote_field = col_names_indexes[self.columns_mapping["vote_column"]]

    def sort_rows_by_voter_id(self):
        data = [self.sheet.row_values(i) for i in range(self.sheet.nrows)]
        data = data[self.first_row :]
        self.data = natsorted(data, key=lambda x: x[self.col["voter_id"]])

    def get_votes(self):
        self.open_excel_sheet()
        self.check_if_no_duplicated_rows()
        self.sort_rows_by_voter_id()
        self.iterate_through_rows()
        objects = {
            "votes_data_per_district": self.votes_data_per_district,
        }
        self.save_mappings_as_jsons(objects)

    def check_if_vote_is_valid(self, row_data):
        if self.only_valid_votes:
            return True
        if row_data[self.col["if_valid"]] == self.valid_value:
            return True

    def check_if_no_duplicated_rows(self):
        all_rows = set()
        for row in range(1, self.sheet.nrows):
            row_values = self.sheet.row_values(row)
            if any(row_values):
                row_values = [str(value) for value in row_values]
                row_txt = "".join(row_values)
                if row_txt in all_rows:
                    raise RuntimeError(f"There is a duplicated row! {row_values}")
                all_rows.add(row_txt)

    def handle_poznan_district(self, district):
        if district == "Projekt ogólnomiejski w ramach Zielonego Budżetu":
            return "Projekty ogólnomiejskie w ramach Zielonego Budżetu"
        if district == "Projekt ogólnomiejski":
            return "Projekty ogólnomiejskie"
        return district.split("-")[0].strip()

    def handle_lodz_district(self, project_id):
        district = project_id[-2:]
        if district.isnumeric():
            return "LL"
        return district

    def handle_lublin_district(self, vote, district):
        neighborhood = district
        vote = vote.replace(" ", "")
        if vote[0].lower() == "o":
            district = "CITYWIDE"
        elif vote[0].lower() == "d":
            district = "LOCAL"
        else:
            self.logger.error("Lublin, vote other than D or O!")
        return district, vote, neighborhood

    def handle_multiple_rows(self, idx, row, voter_id):
        col_name = "subdistrict" if self.col.get("subdistrict") else "district"

        vote = row[self.vote_field]

        neighborhood = None

        if self.unit == "Kraków":
            district = self.project_district_mapping[vote]
        else:
            district = row[self.col[col_name]]

        # EXCEPTIONS / ERRORS IN FILES

        if self.instance == 2020 and self.unit == "Łódź" and vote == "P135KR":
            district = "BD"

        if self.unit == "Lublin":
            district, vote, neighborhood = self.handle_lublin_district(vote, district)

        if self.district_name_mapping:
            if self.unit == "Poznań":
                district = self.handle_poznan_district(district)
            if self.unit == "Łódź" and self.instance >= 2022:
                district = self.handle_lodz_district(district)
            district = self.district_district_name_mapping[district]

        if self.no_points:
            self.voter_votes[district].append(vote)
        else:
            points = int(row[self.points_field])
            self.voter_votes[district].append([vote, points])

        try:
            valid = False
            counter = 0
            while not valid:
                counter += 1
                next_row = self.data[idx + counter]
                valid = self.check_if_vote_is_valid(next_row)
            next_voter = self.data[idx + counter][self.col["voter_id"]]
            if self.voter_id_integer:
                next_voter = int(next_voter)
        except IndexError:
            next_voter = None
        if str(voter_id) != str(next_voter):
            voter_item = self.create_voter_item(row, voter_id, neighborhood)
            if self.no_points:
                self.handle_multiple_rows_no_points(voter_item)
            else:
                self.handle_multiple_rows_with_points(voter_item)

    def get_neighborhood_from_districts_list(self):
        districts = list(self.voter_votes.keys())
        if len(districts) == 1 and "CITYWIDE" not in districts:
            return districts[0]
        if len(districts) == 2 and "CITYWIDE" in districts:
            districts.remove("CITYWIDE")
            return districts[0]

    def handle_multiple_rows_with_points(self, voter_item):
        voter_item.neighborhood = self.get_neighborhood_from_districts_list()
        for district, votes in self.voter_votes.items():
            district_upper = utils.change_district_into_name(district)
            sorted_votes = sorted(votes, key=lambda x: x[1], reverse=True)
            voter_item_cp = deepcopy(voter_item)
            votes = [el[0] for el in sorted_votes]
            points = [str(el[1]) for el in sorted_votes]
            voter_item_cp.vote = ",".join(votes)
            voter_item_cp.points = ",".join(points)
            self.votes_data_per_district[district_upper].append(vars(voter_item_cp))
        self.voter_votes = collections.defaultdict(list)

    def handle_multiple_rows_no_points(self, voter_item):
        for district, votes in self.voter_votes.items():
            district_upper = utils.change_district_into_name(district)
            voter_item_cp = deepcopy(voter_item)
            voter_item_cp.vote = ",".join(votes)
            self.votes_data_per_district[district_upper].append(vars(voter_item_cp))
        self.voter_votes = collections.defaultdict(list)

    def iterate_through_rows(self):
        for idx, row_data in enumerate(self.data):
            valid = self.check_if_vote_is_valid(row_data)
            if valid:
                if self.voter_id_integer:
                    voter_id = int(row_data[self.col["voter_id"]])
                if not voter_id:
                    return
                self.handler(idx, row_data, voter_id)
            # TODO if does not log, why?
            if idx + 1 % 10000 == 0:
                self.logger.info(f"{idx + 1} lines of votes processed")

    def add_optional_columns_to_voter(self, item, row):
        if self.get_age:
            item.add_age(row[self.col["age"]])
        if self.get_sex:
            item.add_sex(row[self.col["sex"]])
        if self.get_voting_method:
            item.add_voting_method(row[self.col["voting_method"]])
        return item

    def get_voter_district(self, row, voter_id):
        if self.col.get("subdistrict"):
            district = row[self.col["subdistrict"]]
        else:
            district = row[self.col["district"]]
        if self.district_name_mapping:
            if self.unit == "Poznań":
                district = self.handle_poznan_district(district)
            elif self.unit == "Łódź" and self.instance >= 2022:
                district = self.handle_lodz_district(district)
            district = self.district_district_name_mapping[district]
        if self.unit == "Warszawa":
            # TODO
            district_votes = row[self.district_columns["local"]]
            if district_votes:
                if isinstance(district_votes, float):
                    project_id = str(int(district_votes))
                else:
                    districts = set()
                    districts_dict = dict()
                    for project_id in district_votes.split(","):
                        district = self.project_district_mapping[project_id]
                        districts_dict[district] = districts_dict.get(district, 0) + 1
                        districts.add(district)
                    if len(districts) > 1:
                        self.logger.warning(
                            f"Voter: {voter_id} has more than one district! "
                            f"Vote: {district_votes} districts: {districts} "
                            f"Counter: {districts_dict}"
                        )
                # else:
                #     project_id = district_votes.split(",")[0]
                # district = self.project_district_mapping[project_id]
        if district not in ("", "---"):
            return district

    def create_voter_item(self, row, voter_id, neighborhood=None):
        item = VoterItem(voter_id)
        if self.col.get("district"):
            item.district = self.get_voter_district(row, voter_id)
            if neighborhood:
                item.add_neighborhood(neighborhood)
            else:
                item.add_neighborhood(item.district)
        item = self.add_optional_columns_to_voter(item, row)
        return item

    def clean_votes_field(self, votes):
        if isinstance(votes, float):
            return int(votes)
        votes = votes.replace(" ", "")
        return votes

    def handle_one_row_no_points(self, _, row, voter_id):
        voter_item = self.create_voter_item(row, voter_id)
        unit_votes = row[self.col["unit_votes"]]
        if unit_votes and unit_votes not in utils.wrong_votes:
            voter_item.vote = self.clean_votes_field(unit_votes)
            self.votes_data_per_district["CITYWIDE"].append(vars(voter_item))
        for subdistrict, column_index in self.district_columns.items():
            district_votes = row[column_index]
            neighborhood = voter_item.neighborhood or subdistrict
            if district_votes and district_votes not in utils.wrong_votes:
                voter_item_cp = deepcopy(voter_item)
                voter_item_cp.vote = self.clean_votes_field(district_votes)
                if self.subdistricts:
                    if not self.votes_data_per_district.get(neighborhood):
                        self.votes_data_per_district[neighborhood] = (
                            collections.defaultdict(list)
                        )
                    self.votes_data_per_district[neighborhood][subdistrict].append(
                        vars(voter_item_cp)
                    )
                else:
                    self.votes_data_per_district[neighborhood].append(
                        vars(voter_item_cp)
                    )
