import ast
import collections
import csv
from copy import deepcopy
from dataclasses import dataclass

from natsort import natsorted

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
                vote_data = row["project_id"]
                if vote_name == "vote_rankings_clean":
                    # it's ordinal, so we need projects and rankigs
                    vote_data = [row["project_id"], row["rank"]]
                elif vote_name == "vote_tokens_clean":
                    # it's cumulative, so we need projects and points
                    vote_data = [row["project_id"], row["tokens"]]
                vote[row["election_id"]][row["voter_id"]].append(vote_data)
            all_votes[vote_name] = vote
        return all_votes

    def load_projects_per_election(self):
        self.elections_with_map_geometry = set()
        self.elections_with_categories = set()
        projects_per_election = collections.defaultdict(list)
        projects_reader = csv.DictReader(open(self.projects))
        for row in projects_reader:
            if row["map_geometry"]:
                # We want to add coordinates only to these projects where it exists
                self.elections_with_map_geometry.add(row["election_id"])
            elif row["category_id"]:
                self.elections_with_categories.add(row["election_id"])
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

    def handle_voter_vote(self, voter_id, votes):
        voter = self.voters[voter_id]
        if voter[0]["void"] != "0":
            raise RuntimeError(
                f"Voter `{voter_id}` has a void vote! "
                f"Should be removed! Election ID: {self.election_id}"
            )

        voter_item = VoterItem(voter_id)
        if self.vote_type in ("approval"):
            for vote in votes:
                self.all_projects_votes["votes"][vote] = self.all_projects_votes["votes"].get(vote, 0) + 1
        elif self.vote_type in ("cumulative", "ordinal"):
            points = [vote[1] for vote in votes]
            votes = [vote[0] for vote in votes]
            zipped = zip(votes, points)

            # TODO to confirm: of 1 is the best rank:
            # if self.vote_type == "ordinal":
            #     votes = natsorted(zipped, key=lambda x: x[1])
            # else:
            votes = natsorted(zipped, key=lambda x: x[1], reverse=True)
            points = [vote[1] for vote in votes]
            votes = [vote[0] for vote in votes]
            if self.vote_type == "cumulative":
                # not needed in ordinal as it's a ranking
                voter_item.points = ",".join(points)
            elif self.vote_type == "ordinal":
                if len(points) != len(set(points)):
                    text = (
                        f"Election ID: {self.election_id}, vote name: "
                        f"{self.vote_name} voter ID:  {voter_id} has two same"
                        f" rankings!!\n votes: {votes}, rankings: {points}"
                    )
                    # raise RuntimeError(text)
                    self.logger.info(text)
                    return
            for vote, point in zip(votes, points):
                # if int(self.election_id) == 16:
                #     if int(vote) == 237:
                #         print(vote, point)
                self.all_projects_votes["votes"][vote] = self.all_projects_votes["votes"].get(vote, 0) + 1
                self.all_projects_votes["score"][vote] = self.all_projects_votes["score"].get(vote, 0) + int(point)

            # if int(self.election_id) == 16:
            #     print(self.all_projects_votes["score"].get('237'))

        voter_item.vote = ",".join(votes)

        return voter_item

    def create_all_voters_dict(self, vote_data):
        all_voters = []
        for voter_id, votes in vote_data[self.election_id].items():
            voter_item = self.handle_voter_vote(voter_id, votes)
            if voter_item:
                all_voters.append(voter_item)
        return all_voters

    def sort_projects_by_results(projects, score_field="votes"):
        projects = dict(
            sorted(
                projects.items(),
                key=lambda x: int(x[1][score_field]),
                reverse=True,
            )
        )
        return projects

    def add_project_votes(self, all_projects, score):
        for project in all_projects:
            try:
                project.votes = self.all_projects_votes["votes"][project.project_id]
            except KeyError:
                # self.logger.info(
                #     f"Project: {project.project_id} does not have any votes!\n"
                #     f"Election instance: {self.instance}, election name: {vote_name}")
                # we want to keep them anyway, cause they were available to vote for
                project.votes = 0
            if score:
                project.score = self.all_projects_votes["score"][project.project_id]
        return all_projects

    def get_vote_type(self):
        if self.vote_name == "vote_approvals":
            self.vote_type = "approval"
            # handle approvals, so only selected projects, without any particular order
        elif self.vote_name == "vote_infer_knapsack_partial":
            self.vote_type = "approval"
            # approval, with max budget
            # the remaining budget is assigned to the next project in line
            # – allocated is the budget that under this method would be allocated to the project by the voter.
        elif self.vote_name == "vote_infer_knapsack_skip":
            self.vote_type = "approval"
            # approval, with max budget
            # the remaining budget is assigned to the next ranked project that can be fully funded
            # – allocated is the budget that under this method would be allocated to the project by the voter.
        elif self.vote_name == "vote_knapsacks_clean":
            self.vote_type = "approval"
            # approval, with max budget
            # handle approvals, so only selected projects, without any particular order
        elif self.vote_name == "vote_rankings_clean":
            self.vote_type = "ordinal"
            # ordinal, so only correct order ("rank" field, max length 5, check min length)
        elif self.vote_name == "vote_tokens_clean":
            # raise RuntimeError(f"Not wanted file: {self.instance}")
            self.vote_type = "cumulative"
            # cumulative, so votes and score (34,35,12;5,3,2), where tokens are points
            # get tokens
        else:
            raise RuntimeError(f"Not recognized vote type! {self.vote_type}")
        self.all_vote_types[self.vote_name] = self.all_vote_types.get(self.vote_name, 0) + 1

    def iterate_through_elections(self):
        self.all_vote_types = {}
        for election_id, election_data in self.elections_dict.items():
            # vote_type = election_data["phase_0"] # not needed as we have it from file name
            self.election_id = election_id
            self.voters = self.voters_per_election[election_id]
            projects = self.projects_per_election[election_id]
            all_projects = self.create_project_items(projects)
            for vote_name, vote_data in self.all_votes.items():
                self.vote_name = vote_name
                self.all_projects_votes = {"votes": {}, "score": {}}
                if not vote_data.get(str(election_id)):
                    continue
                if vote_name in ("vote_infer_knapsack_partial", "vote_infer_knapsack_skip"):
                    # dont process derived data
                    continue
                self.get_vote_type()

                all_voters = self.create_all_voters_dict(vote_data)

                self.instance = election_data["name"]
                name = f"{self.instance.replace(" ", "_").replace(":", "")}_{vote_name}"
                file_name = f"{self.country}_{self.unit}_{name}"
                file_, csv_file = utils.create_csv_file(file_name)

                # create projects section
                score = True if self.vote_type in ("cumulative", "ordinal") else None

                all_projects = self.add_project_votes(all_projects, score)

                # sort by votes or score
                if score:
                    all_projects.sort(key=lambda x: x.score, reverse=True)
                else:
                    all_projects.sort(key=lambda x: x.votes, reverse=True)

                self.add_projects_section(csv_file, score)

                for project in all_projects:
                    row = [
                        project.project_id,
                        project.cost,
                        project.votes
                    ]
                    if score:
                        row.append(project.score)
                    if election_id in self.elections_with_categories:
                        row.append(project.category)
                    if election_id in self.elections_with_map_geometry:
                        row.extend([project.latitude, project.longitude])
                    csv_file.writerow(row)

                # create votes section

                points = True if self.vote_type == "cumulative" else None
                self.add_votes_section(csv_file, points)
                for voter in all_voters:
                    row = [voter.voter_id, voter.vote]
                    if points:
                        row.append(voter.points)
                    csv_file.writerow(row)

                file_.close()

                self.add_metadata(file_name, election_data)
        # raise RuntimeError(f"Vote types counted: {self.all_vote_types}")

    def add_metadata(self, file_name, election_data):
        # print(election_data)
        path_to_file = utils.get_path_to_file(file_name)

        num_projects_counted, num_votes_counted = utils.count_projects_and_votes(
            path_to_file
        )
        num_projects = election_data["total_n_projects"]

        if int(num_projects) != int(num_projects_counted):
            raise RuntimeError(
                f"Number of projects from file and data does not match!\n"
                f"Counted: {num_projects_counted} vs from data {num_projects}\n"
                f"Vote instance: {self.instance}, vote name: {self.vote_name}"
            )

        # if vote_name == "vote_approvals":
        #     num_votes_field = "exit_off_approval"
        # elif vote_name == "vote_infer_knapsack_partial":
        #     num_votes_field = "exit_off_knapsack"
        # elif vote_name == "vote_infer_knapsack_skip":
        #     num_votes_field = "exit_off_knapsack"
        # elif vote_name == "vote_knapsacks_clean":
        #     num_votes_field = "exit_off_knapsack"
        # elif vote_name == "vote_rankings_clean":
        #     num_votes_field = "exit_off_ranking"
        # elif vote_name == "vote_tokens_clean":
        #     num_votes_field = "exit_exp_token"
        # if election_data.get(num_votes_field):
        #     num_votes = int(float(election_data[num_votes_field].replace(",", ".")))
        # else:
        #     num_votes = 0
        num_votes = election_data["voters_total"]

        if int(num_votes) != int(num_votes_counted):
            # – voters total: number of voters that cast any ballot in this election
            # So it does not always match
            # self.logger.info(
            #     f"Number of votes from file and data does not match!\n"
            #     f"Counted: {num_votes_counted} vs from data {num_votes}\n"
            #     f"Vote instance: {self.instance}, vote name: {self.vote_name}"
            # )
            pass

        budget = int(float(election_data["budget"].replace(",", ".")))
        description = election_data["name"]
        is_real_election = election_data["real_election"]
        # TODO what to do with not real elections (atm only real ones)
        if not is_real_election:
            raise RuntimeError("It's not a real election, not implemented what to do")

        temp_meta = deepcopy(self.metadata)

        metadata = (
            "META\n"
            "key;value\n"
            f"description;{description}\n"
            f"country;{self.country}\n"
            f"unit;{self.unit}\n"
            f"instance;{self.instance}\n"
            f"subunit;{self.vote_name}\n"
            f"num_projects;{num_projects}\n"
            f"num_votes;{num_votes_counted}\n"
            f"vote_type;{self.vote_type}\n"
            f"rule;???\n"
            f"date_begin;??.??.????\n"
            f"date_end;??.??.????\n"
            f"budget;{budget}\n"
            f"language;???\n"
        )

        for key, value in temp_meta.items():
            metadata += f"{key};{value}\n"

        if self.vote_type in ("approval", "ordinal"):
            if self.vote_type == "approval":
                length_field = "setting_off_approval_k_projects"

            elif self.vote_type == "ordinal":
                length_field = "setting_off_ranking_k_projects"
            if self.vote_name in ("vote_infer_knapsack_partial", "vote_infer_knapsack_skip", "vote_knapsacks_clean"):
                # metadata += f"min_sum_cost;???\n"
                metadata += f"max_sum_cost;???\n"
            else:
                max_length = election_data.get("max_n_projects") or election_data.get(length_field)
                if max_length:
                    max_length = int(float(max_length.replace(",", ".")))
                    metadata += f"max_length;{max_length}\n"
                    # TODO something wrong with these values
        elif self.vote_type == "cumulative":
            # metadata += f"min_sum_points;???\n"
            metadata += f"max_sum_points;???\n"

        utils.prepend_line_at_the_beggining_of_file(metadata, path_to_file)

    def add_projects_section(self, csv_file, score=False):
        fields = ["project_id", "cost", "votes"]
        if score:
            fields.append("score")
        if self.election_id in self.elections_with_categories:
            fields.append("category")
        if self.election_id in self.elections_with_map_geometry:
            fields.extend(["latitude", "longitude"])
        csv_file.writerow(["PROJECTS"])
        csv_file.writerow(fields)

    def add_votes_section(self, csv_file, points=False):
        fields = ["voter_id", "vote"]
        if points:
            fields.append("points")
        csv_file.writerow(["VOTES"])
        csv_file.writerow(fields)
