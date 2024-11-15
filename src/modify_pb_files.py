"""Modify and save new .pb files.

This script modifies already created .pb files. It can be used to count
votes / projects, to sort projects by score, to replace commas in floats
or to calculate selected projects from budget value.

It loads pb file (from output directory), makes some changes and (if wanted)
saves new files to output/cleaned dir.
"""

import collections
import csv
import glob
import os
import re
from copy import deepcopy
from dataclasses import dataclass

import pycountry

import helpers.utilities as utils
from helpers.settings import (
    meta_fields_order,
    projects_fields_order,
    votes_fields_order,
)

logger = utils.create_logger()


@dataclass
class ModifyPBFiles:
    input_files_path: str = None
    output_files_path: str = None

    def __post_init__(self):
        pabulib_dir = os.path.join(os.getcwd(), "src")
        if not self.input_files_path:
            self.input_files_path = os.path.join(pabulib_dir, "output", "*.pb")
        if not self.output_files_path:
            self.output_files_path = os.path.join(pabulib_dir, "output", "cleaned")

    def iterate_through_pb_files(self):
        files = glob.glob(self.input_files_path)
        utils.human_sorting(files)
        self.global_data = []
        for idx, pb_file in enumerate(files):
            self.filename = os.path.basename(pb_file)
            logger.info(f"Processing file: {self.filename}")
            (
                self.meta,
                self.projects,
                self.votes,
                # TODO
                self.check_votes,
                self.check_scores,
            ) = utils.load_pb_file(pb_file)
            self.do_some_modifications(idx)
            # IF YOU WANT TO SAVE ONLY MODIFIED FILES
            if self.modified:
                self.save_to_file()
            # self.save_to_file()
            self.modified = False
        for data in self.global_data:
            print(data)

    def update_number_of_votes(self):
        self.meta["num_votes"] = len(self.votes)

    def update_number_of_projects(self):
        self.meta["num_projects"] = len(self.projects)

    def update_projects_votes(self):
        remove_projects_with_no_votes = True
        self.counted_votes = utils.count_votes_per_project(self.votes)
        project_list = [project[0] for project in self.projects.items()]
        for project_id in project_list:
            counted_votes = self.counted_votes.get(project_id)
            if not counted_votes:
                if remove_projects_with_no_votes:
                    logger.critical(
                        "There is a project with no votes! Removing it! "
                        f"File: {self.filename}, project ID: {project_id}"
                    )
                    self.projects.pop(project_id)
                else:
                    # KEEP PROJECTS WITH NO VOTES
                    self.projects[project_id]["votes"] = 0
            else:
                self.projects[project_id]["votes"] = counted_votes

    def update_projects_scores(self):
        if self.meta["vote_type"] in ("cumulative", "ordinal"):
            (_, project_data), *_ = self.projects.items()
            if not project_data.get("score"):
                self.counted_scores = utils.count_points_per_project(self.votes)
                for project_id, score in self.counted_scores.items():
                    self.projects[project_id]["score"] = score
                self.modified = True

        # self.check_scores = True
        # if self.check_scores:
        #     self.counted_scores = utils.count_points_per_project(self.votes)
        #     for project_id, score in self.counted_scores.items():
        #         self.projects[project_id]["score"] = score

    def replace_commas_in_floats(self):
        if "," in self.meta["budget"]:
            self.meta["budget"] = float(self.meta["budget"].replace(",", "."))
            self.modified = True
        if self.meta.get("max_sum_cost"):
            if "," in self.meta["max_sum_cost"]:
                self.meta["max_sum_cost"] = float(
                    self.meta["max_sum_cost"].replace(",", ".")
                )
                self.modified = True
        for project_number, project_data in self.projects.items():
            cost = project_data["cost"]
            if not isinstance(cost, int):
                if "," in cost:
                    self.projects[project_number]["cost"] = float(
                        cost.replace(",", ".")
                    )
                    self.modified = True

    def sort_projects_by_score(self):
        first_project_dict = next(iter(self.projects.values()))
        if "score" in first_project_dict:
            score_field = "score"
        else:
            score_field = "votes"
        self.projects = dict(
            sorted(
                self.projects.items(),
                key=lambda x: int(x[1][score_field]),
                reverse=True,
            )
        )

    def do_some_modifications(self, idx):
        self.modified = False  # set it to True if you want to save new file
        # self.remove_projects_with_no_cost()
        # self.remove_projects_with_no_votes()
        # self.update_projects_votes()
        # self.update_number_of_votes()
        # self.update_number_of_projects()
        # self.update_projects_scores()
        # self.replace_commas_in_floats()
        # self.replace_semicolons_in_votes()
        # self.add_selected_to_projects_section(idx)
        # self.calculate_selected_from_budget()
        # self.change_voters_sex()
        # self.projects = utils.sort_projects_by_results(self.projects)
        # self.change_year_into_dates()
        # self.add_fully_funded()
        # self.add_currency()
        # self.add_description()
        # self.change_type_into_choose_1()
        # self.get_all_used_comments()
        # self.change_description()
        # self.modify_zurich_files()
        # self.modify_mechanical_turk_files()
        # self.remove_scores_from_approvals()
        # self.standarize_category_column_in_projects()
        # self.check_dates()
        # self.change_true_flags_to_1()
        # self.modify_stanford_files()
        # self.check_language_and_currency_codes()
        # self.check_comment_iteration()
        # self.change_warsaw_and_czestochowa()

    def change_warsaw_and_czestochowa(self):
        # description = self.meta["description"]
        # if "Warsaw" in description:
        #     description = description.replace("Warsaw", "Warszawa")
        #     self.meta["description"] = description
        #     self.modified = True
        # elif self.meta["unit"] == "Czestochowa":
        #     self.meta["unit"] = "Częstochowa"
        #     self.modified = True
        district = self.meta.get("district")
        subunit = self.meta.get("subunit")
        description = self.meta["description"]
        if district and district.isupper():
            self.meta["district"] = district.title()
            self.meta["description"] = description.replace(district, district.title())
            self.modified = True
        if subunit and subunit.isupper():
            self.meta["subunit"] = subunit.title()
            self.meta["description"] = description.replace(subunit, subunit.title())
            self.modified = True

    def check_comment_iteration(self):
        comment = self.meta.get("comment")
        if comment:
            if not comment.startswith("#1: "):
                self.meta["comment"] = f"#1: {comment}"
                self.modified = True

    def check_language_and_currency_codes(self):
        language_code_mapping = {
            "polish": "pl",
            "english": "en",
            "french": "fr",
            "Dutch": "nl",
        }

        language_code = self.meta.get("language")
        if language_code:
            # Check if the language code is in ISO 639-1 format (two-letter code).
            if pycountry.languages.get(alpha_2=language_code) is None:
                try:
                    language_code = language_code_mapping[language_code]
                    self.meta["language"] = language_code
                    self.modified = True
                except KeyError:
                    raise RuntimeError(f"language_code: {language_code}")

        currency_code_mapping = {}

        currency_code = self.meta.get("currency")
        if currency_code:
            # Check if the language code is in ISO 639-1 format (two-letter code).
            if pycountry.currencies.get(alpha_3=currency_code) is None:
                try:
                    currency_code = currency_code_mapping[currency_code]
                    self.meta["currency"] = currency_code
                    self.modified = True
                except KeyError:
                    raise RuntimeError(f"currency_code: {currency_code}")

    def modify_stanford_files(self):
        vote_type = self.meta["vote_type"]
        if vote_type != "approval":
            self.global_data.append(self.meta["description"])

    def change_true_flags_to_1(self):
        fully_funded = self.meta.get("fully_funded")
        if fully_funded:
            if fully_funded == "true":
                self.meta["fully_funded"] = "1"
                self.modified = True

        experimental = self.meta.get("experimental")
        if experimental:
            if experimental == "true":
                self.meta["experimental"] = "1"
                self.modified = True

    def check_dates(self):
        date_begin = self.meta["date_begin"]
        date_end = self.meta["date_end"]

        pattern = re.compile(r"\d{1,2}.\d{1,2}.\d{4}")

        for date in [date_begin, date_end]:
            if pattern.match(date):
                return
            if "." not in str(date) and len(str(date)) == 4:
                return
            raise RuntimeError(f"date `{date}` do not match the pattern")

    def standarize_category_column_in_projects(self):
        (_, project_data), *_ = self.projects.items()
        if project_data.get("categories"):
            self.modified = True

    def remove_scores_from_approvals(self):
        if self.meta["vote_type"] == "approval":
            (_, project_data), *_ = self.projects.items()
            if project_data.get("score"):
                for project_id, project_data in self.projects.items():
                    del project_data["score"]
                self.modified = True

    def modify_mechanical_turk_files(self):
        self.meta["language"] = "en"
        self.meta["country"] = "Worldwide"
        self.meta["experimental"] = "1"
        self.modified = True

    def modify_zurich_files(self):
        for date in ["date_begin", "date_end"]:
            file_date = self.meta[date]
            y, m, d = file_date.split("-")
            self.meta[date] = f"{d}.{m}.{y}"
        self.modified = True
        self.meta["acknowledgments"] = self.meta.pop("comment")
        self.meta["instance"] = self.filename.split("_")[-1].split(".")[0]
        self.meta["experimental"] = "1"

    def change_description(self):
        district = self.meta["subunit"]
        unit = self.meta["unit"]
        if unit == "Warszawa":
            unit = "Warsaw"
        self.meta["description"] = f"District PB in {unit}, {district}"
        self.modified = True

    def get_all_used_comments(self):
        if self.meta.get("comment"):
            comment = self.meta["comment"]
            # self.edit_comment(comment)
            # comments are enumerated with `#n:` where n means comment number
            split_pattern = r"#\d+:\s(.*?)"
            comments = re.split(split_pattern, comment)
            comments = [comment.strip() for comment in comments if comment]
            for comment in comments:
                if comment:
                    self.comments[comment].append(self.filename)

    def edit_comment(self, comment):
        if comment == "#1: Actual comment.":
            comment = "#1: New comment."
        # elif not comment.startswith("#1: "):
        #     comment = f"#1: {comment}"

        self.meta["comment"] = comment
        self.modified = True

    def change_type_into_choose_1(self):
        if self.meta["vote_type"] == "approval":
            if self.meta.get("max_length"):
                if int(self.meta["max_length"]) == 1:
                    self.counter.append(
                        [self.meta["description"], self.meta["instance"]]
                    )
                    self.meta["vote_type"] = "choose-1"
                    self.modified = True

    def update_meta(self):
        if self.meta.get("comments"):
            comment = self.meta.pop("comments")
            self.meta["comment"] = comment

    def sort_meta_fields(self):
        # TODO nie ogarnie additional keys, tych co nie ma w mappingu
        known_fileds = {
            key: self.meta[key] for key in meta_fields_order if key in self.meta
        }
        additional_fields = {
            key: self.meta[key] for key in self.meta if key not in meta_fields_order
        }

        self.meta = known_fileds | additional_fields

    def get_all_fields(self):
        meta_fileds = self.meta.keys()
        projects_fileds = next(iter(self.projects.items()))[1].keys()
        votes_fields = next(iter(self.votes.items()))[1].keys()
        self.all_meta_fields.update(meta_fileds)
        self.all_projects_fields.update(projects_fileds)
        self.all_votes_fields.update(votes_fields)

    def add_description(self):
        if not self.meta.get("description"):
            district = self.meta["district"]
            subunit = self.meta["subunit"]
            unit = self.meta["unit"]
            if district == subunit:
                description = f"District PB in Warszawa, {district}"
            else:
                description = f"Local PB in Warszawa, {district} | {subunit}"
            # if district == subunit:
            #     description = f'District PB in {unit}, {district}'
            # else:
            #     description = f'Local PB in {unit}, {district} | {subunit}'
            self.meta["description"] = description
            self.modified = True

    def add_currency(self):
        country = self.meta["country"]
        if country == "Poland":
            currency = "PLN"
        elif country in ("Netherlands", "France"):
            currency = "EUR"
        elif country == "Artificial":
            currency = "USD"
        else:
            raise RuntimeError(f"I dont know this country: {country}")
        self.meta["currency"] = currency

    def add_fully_funded(self):
        budget = self.meta["budget"]
        projects = [project for project in self.projects.values()]
        fully_funded = utils.check_if_fully_funded(budget, projects)
        if fully_funded:
            self.meta["fully_funded"] = 1
            logger.info(f"Added fully funded tag to {self.filename}")
            self.modified = True

    def change_year_into_dates(self):
        year = self.meta.pop("year")
        self.meta["date_begin"] = year
        self.meta["date_end"] = year

    def change_voters_sex(self):
        new_votes = {}
        for voter, voter_dict in self.votes.items():
            new_voter_dict = deepcopy(voter_dict)
            if voter_dict["sex"] == "K":
                new_voter_dict["sex"] = "F"
            new_votes[voter] = new_voter_dict
        self.votes = new_votes

    def remove_projects_with_no_votes(self):
        self.projects = {
            project_id: project_dict
            for project_id, project_dict in self.projects.items()
            if int(project_dict["votes"] or 0) != 0
        }

    def remove_projects_with_no_cost(self):
        self.projects = {
            project_id: project_dict
            for project_id, project_dict in self.projects.items()
            if int(project_dict["cost"] or 0) != 0
        }

    def calculate_selected_from_budget(self):
        # be sure projects are sorted by score!
        self.projects = utils.sort_projects_by_results(self.projects)

        budget = float(self.meta["budget"])

        for project_id, project_dict in self.projects.items():
            selected = 0
            project_cost = float(project_dict["cost"])
            if budget > project_cost:
                selected = 1
                budget -= project_cost
            self.projects[project_id]["selected"] = selected

    def add_selected_to_projects_section(self, idx):
        if idx == 0:
            country = "Poland"
            city = "Kraków"
            year = "2019"
            file_name = f"{country}_{city}_{year}_projects_dict_per_district"
            self.project_selected_mapping = (
                utils.create_project_selected_mapping_by_district(file_name)
            )
        district = self.meta.get("district", "OGÓLNOMIEJSKIE")
        for project, project_dict in self.projects.items():
            selected = self.project_selected_mapping[district][project]
            project_dict["selected"] = selected
            self.projects[project] = project_dict

    def replace_semicolons_in_votes(self):
        for vote, vote_dict in self.votes.items():
            input_vote = vote_dict["vote"]
            changed_vote = input_vote.replace(";", ",")
            self.votes[vote]["vote"] = changed_vote

    def write_votes_section(self, writer):
        writer.writerow(["VOTES"])
        save_headers = True
        for voter_id, vote in self.votes.items():
            sorted_fields = self.sort_votes_fields(vote)
            if save_headers:
                votes_headers = list(sorted_fields.keys())
                # if 'categories' in votes_headers:
                #     votes_headers = list(map(lambda x: x.replace(
                #         'categories', 'category'), votes_headers))
                writer.writerow(["voter_id"] + votes_headers)
                save_headers = False
            writer.writerow([voter_id] + list(sorted_fields.values()))

    def write_meta_section(self, writer):
        self.update_meta()
        self.sort_meta_fields()

        writer.writerow(["META"])
        writer.writerow(["key", "value"])

        for key, value in self.meta.items():
            writer.writerow([key, value])

    def sort_projects_fields(self, project_info):
        known_fields = {
            key: project_info[key]
            for key in projects_fields_order
            if key in project_info
        }
        additional_fields = {
            key: project_info[key]
            for key in project_info
            if key not in projects_fields_order
        }
        return known_fields | additional_fields

    def sort_votes_fields(self, vote):
        known_fields = {key: vote[key] for key in votes_fields_order if key in vote}
        additional_fields = {
            key: vote[key] for key in vote if key not in votes_fields_order
        }
        return known_fields | additional_fields

    def write_projects_section(self, writer):
        writer.writerow(["PROJECTS"])
        save_headers = True
        for project_id, project_info in self.projects.items():
            sorted_fields = self.sort_projects_fields(project_info)
            del sorted_fields["id"]
            if save_headers:
                project_headers = list(sorted_fields.keys())
                if "categories" in project_headers:
                    project_headers = list(
                        map(
                            lambda x: x.replace("categories", "category"),
                            project_headers,
                        )
                    )
                writer.writerow(["project_id"] + project_headers)
                save_headers = False
            writer.writerow([project_id] + list(sorted_fields.values()))

    def save_to_file(self):
        pb_file = os.path.join(self.output_files_path, self.filename)
        with open(pb_file, "a+", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            self.write_meta_section(writer)
            self.write_projects_section(writer)
            self.write_votes_section(writer)

    def run_pre_iteration(self):
        self.comments = collections.defaultdict(list)
        self.counter = []

    def run_post_iteration(self):
        # print("hakuna!", len(self.counter))
        # for desc, instance in self.counter:
        #     print(desc, instance)
        for comment, files in self.comments.items():
            print(comment, files, sep="\n")

    def start(self):
        self.run_pre_iteration()
        self.iterate_through_pb_files()
        self.run_post_iteration()


mpbf = ModifyPBFiles()
mpbf.start()
