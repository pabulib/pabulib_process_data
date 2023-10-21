"""Modify and save new .pb files.

This script modifies already created .pb files. It can be used to count
votes / projects, to sort projects by score, to replace commas in floats
or to calculate selected projects from budget value.

It loads pb file (from output directory), makes some changes and (if wanted)
saves new files to output/cleaned dir.
"""


import csv
import glob
import os
from copy import deepcopy
from dataclasses import dataclass

import helpers.utilities as utils

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
            self.output_files_path = os.path.join(
                pabulib_dir, "output", "cleaned")

    def iterate_through_pb_files(self):
        files = glob.glob(self.input_files_path)
        utils.human_sorting(files)
        for idx, pb_file in enumerate(files):
            self.filename = os.path.basename(pb_file)
            logger.info(f'Processing file: {self.filename}')
            (
                self.meta,
                self.projects,
                self.votes,
                self.check_scores,
            ) = utils.load_pb_file(pb_file)
            self.do_some_modifications(idx)
            # IF YOU WANT TO SAVE ONLY MODIFIED FILES
            if self.modified:
                self.save_to_file()
            # self.save_to_file()
            self.modified = False

    def update_number_of_votes(self):
        self.meta["num_votes"] = len(self.votes)

    def update_number_of_projects(self):
        self.meta["num_projects"] = len(self.projects)

    def update_projects_votes(self):
        remove_projects_with_no_votes = True
        self.counted_votes = utils.count_votes_per_project(self.votes)
        updated_projects = self.projects.copy()
        for project_id in self.projects:
            counted_votes = self.counted_votes.get(project_id)
            if not counted_votes:
                if remove_projects_with_no_votes:
                    logger.critical(
                        'There is a project with no votes! Removing it! '
                        f'File: {self.filename}, project ID: {project_id}'
                    )
                    updated_projects.pop(project_id)
                else:
                    # KEEP PROJECTS WITH NO VOTES
                    updated_projects[project_id]["votes"] = 0
            else:
                updated_projects[project_id]["votes"] = counted_votes

        self.projects = updated_projects.copy()

    def update_projects_scores(self):
        if self.check_scores:
            self.counted_scores = utils.count_points_per_project(self.votes)
            for project_id, score in self.counted_scores.items():
                self.projects[project_id]["score"] = score

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
        self.modified = True  # set it to True if you want to save new file
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
        self.projects = utils.sort_projects_by_results(self.projects)
        self.change_year_into_dates()

    def change_year_into_dates(self):
        year = self.meta.pop('year')
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
        self.projects = {project_id: project_dict for project_id,
                         project_dict in self.projects.items() if int(project_dict['votes'] or 0) != 0}

    def remove_projects_with_no_cost(self):
        self.projects = {project_id: project_dict for project_id,
                         project_dict in self.projects.items() if int(project_dict['cost'] or 0) != 0}

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
        votes_headers = ["voter_id"] + \
            list(self.votes[next(iter(self.votes))].keys())
        writer.writerow(votes_headers)
        for voter_id, vote in self.votes.items():
            writer.writerow([voter_id] + list(vote.values()))

    def write_meta_section(self, writer):
        writer.writerow(["META"])
        writer.writerow(["key", "value"])
        for key, value in self.meta.items():
            writer.writerow([key, value])

    def write_projects_section(self, writer):
        writer.writerow(["PROJECTS"])
        projects_headers = ["project_id"] + list(
            self.projects[next(iter(self.projects))].keys()
        )
        writer.writerow(projects_headers)
        for project_id, project_info in self.projects.items():
            writer.writerow([project_id] + list(project_info.values()))

    def save_to_file(self):
        pb_file = os.path.join(self.output_files_path, self.filename)
        with open(pb_file, "a+", newline="", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            self.write_meta_section(writer)
            self.write_projects_section(writer)
            self.write_votes_section(writer)


mpbf = ModifyPBFiles()
mpbf.iterate_through_pb_files()
