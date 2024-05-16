import ast
import collections
import csv
import os
from copy import deepcopy
from dataclasses import dataclass

import helpers.utilities as utils
from helpers import settings
from process_data.base_config import BaseConfig
from process_data.models import ProjectItem, VoterItem


@dataclass
class ProcessData(BaseConfig):
    data_dir: str
    metadata: dict

    def set_up_file_paths(self, csv_files_path):
        # elections
        self.elections = f"{csv_files_path}/elections_rich.csv"

        # projects
        self.projects = f"{csv_files_path}/projects_clean.csv"

        # votes
        self.votes = {
            "vote_approvals": f"{csv_files_path}/vote_approvals_clean.csv",
            "vote_infer_knapsack_partial": f"{csv_files_path}/vote_infer_knapsack_partial.csv",
            "vote_infer_knapsack_skip": f"{csv_files_path}/vote_infer_knapsack_skip.csv",
            "vote_knapsacks_clean": f"{csv_files_path}/vote_knapsacks_clean.csv",
            "vote_rankings_clean": f"{csv_files_path}/vote_rankings_clean.csv",
            "vote_tokens_clean": f"{csv_files_path}/vote_tokens_clean.csv",
        }

        # voters
        self.voters = f"{csv_files_path}/voters_clean.csv"

    def load_elections(self):
        elections_reader = csv.DictReader(open(self.elections))
        return {row["election_id"]: row for row in elections_reader}

    def load_voters_per_election(self):
        voters_per_election = {}
        voters_reader = csv.DictReader(open(self.voters))
        for row in voters_reader:
            election_id = str(row["election_id"])
            if not voters_per_election.get(election_id):
                voters_per_election[election_id] = collections.defaultdict(list)
            voters_per_election[election_id][row["voter_id"]].append(row)
        return voters_per_election

    def load_all_votes(self):
        all_votes = {}
        for vote_name, vote_path in self.votes.items():
            vote = {}
            vote_reader = csv.DictReader(open(vote_path))
            for row in vote_reader:
                if not vote.get(row["election_id"]):
                    vote[row["election_id"]] = collections.defaultdict(list)
                vote[row["election_id"]][row["voter_id"]].append(row["project_id"])
            all_votes[vote_name] = vote
        return all_votes

    def load_projects_per_election(self):
        projects_per_election = collections.defaultdict(list)
        projects_reader = csv.DictReader(open(self.projects))
        for row in projects_reader:
            projects_per_election[row["election_id"]].append(row)
        return projects_per_election

    def load_data_from_files(self):
        self.elections_dict = self.load_elections()
        self.voters_per_election = self.load_voters_per_election()
        self.all_votes = self.load_all_votes()
        self.projects_per_election = self.load_projects_per_election()

    def start(self):
        csv_files_path = settings.get_path_to_excel_files(
            self.unit, extra_dir=self.data_dir
        )
        self.logger.info(f"CSV files are located in {csv_files_path} ...")
        self.set_up_file_paths(csv_files_path)
        self.load_data_from_files()
        self.iterate_through_elections()

    def create_project_items(self, projects):
        all_projects = []
        for project in projects:
            project_id = project["project_id"]
            item = ProjectItem(project_id)
            category = project.get("category_id")
            if category:
                item.category = int(category.replace(".0", ""))
            item.cost = project["cost"]
            map_geometry = project.get("map_geometry")
            if map_geometry:
                map_geometry = ast.literal_eval(map_geometry)
                if isinstance(map_geometry[0], dict):
                    map_geometry = map_geometry[0]["coordinates"]
                coordinates = [float(sum(col)) / len(col) for col in zip(*map_geometry)]

                item.latitude, item.longitude = coordinates
            all_projects.append(item)
        return all_projects

    def iterate_through_elections(self):
        for election_id, election_data in self.elections_dict.items():
            voters = self.voters_per_election[election_id]
            projects = self.projects_per_election[election_id]
            all_projects = self.create_project_items(projects)
            for vote_name, vote_data in self.all_votes.items():
                if vote_data.get(election_id):
                    print(vote_name)
                    all_voters = []
                    for voter_id, votes in vote_data[election_id].items():
                        voter = voters[voter_id]
                        if voter[0]["void"] != "0":
                            raise RuntimeError(
                                f"Voter `{voter_id}` has a void vote! "
                                f"Should be removed! Election ID: {election_id}"
                            )
                        voter_item = VoterItem(voter_id)
                        voter_item.vote = ",".join(votes)
                        if vote_name == "vote_approvals":
                            # "vote_infer_knapsack_partial"
                            # "vote_infer_knapsack_skip"
                            # "vote_knapsacks_clean"
                            # "vote_rankings_clean"
                            # "vote_tokens_clean"
                            all_voters.append(voter_item)
                        # elif vote_name == ""
                    # print(all_voters)
                    # create file
                    # file_name = f"{self.country}_{self.unit}_{self.instance}_{vote_name}"
                    file_name = f"{self.unit}_{vote_name}"
                    file_, csv_file = utils.create_csv_file(file_name)

                    # order projects by score / votes
                    # self.sort_projects(e_number, save_points)

                    # create projects section
                    self.add_projects_section(csv_file)

                    for project in all_projects:
                        row = [
                            project.project_id,
                            project.cost,
                            project.category,
                            project.latitude,
                            project.longitude,
                        ]
                        csv_file.writerow(row)

                    # create votes section
                    self.add_votes_section(csv_file)
                    for voter in all_voters:
                        row = [voter.voter_id, voter.vote]
                        csv_file.writerow(row)

                    file_.close()

                    # metadata = self.metadata
                    self.add_metadata(file_name, election_data, vote_name)

    def add_metadata(self, file_name, election_data, vote_name):
        print(election_data)
        path_to_file = utils.get_path_to_file(file_name)
        num_projects_counted, num_votes = utils.count_projects_and_votes(path_to_file)
        num_projects = election_data["total_n_projects"]

        if int(num_projects) != int(num_projects_counted):
            raise RuntimeError(
                f"Number of projects from file and data does not match!\n"
                f" Counted: {num_projects_counted} vs from data {num_projects}"
            )

        max_length = election_data.get("max_n_projects") or election_data.get(
            "setting_off_approval_k_projects"
        )
        budget = int(float(election_data["budget"].replace(",", ".")))
        description = election_data["name"]
        is_real_election = election_data["real_election"]
        voters_total = election_data["voters_total"]

        temp_meta = deepcopy(self.metadata)

        metadata = (
            "META\n"
            "key;value\n"
            f"description;{description}\n"
            f"country;{self.country}\n"
            f"unit;{self.unit}\n"
            f"instance;{self.instance}\n"
            f"num_projects;{num_projects}\n"
            f"num_votes;{num_votes}\n"
            f"vote_type;{vote_name}\n"
            f"budget;{budget}\n"
        )

        for key, value in temp_meta.items():
            metadata += f"{key};{value}\n"

        # num_projects, num_votes = utils.count_projects_and_votes(path_to_file)
        utils.prepend_line_at_the_beggining_of_file(metadata, path_to_file)
        raise RuntimeError

    def add_projects_section(self, csv_file):
        fields = ["project_id", "cost", "category", "latitude", "longitude"]
        csv_file.writerow(["PROJECTS"])
        csv_file.writerow(fields)

    def add_votes_section(
        self,
        csv_file,
    ):
        fields = ["voter_id", "vote"]
        csv_file.writerow(["VOTES"])
        csv_file.writerow(fields)
