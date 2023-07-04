import glob
import os
from collections import defaultdict
from dataclasses import dataclass

import helpers.utilities as utils
from helpers.settings import output_path

logger = utils.create_logger()


@dataclass
class CheckOutputFiles:
    """A class used to check data consistency in .pb files.

    As default takes files from output/ directory, but pattern which
    files to check could be set, for example all flies from
    output directory (files_in_output_dir = 'cleaned/*') or only particular
    city (files_in_output_dir = 'Poland_Katowice_*'). Absolute path to
    files also could be set.

    By default, it logs all checks on terminal, but if create_txt_report set
    to true, report will be saved as txt file.

    Attributes
    ----------
    files_in_output_dir : str, default: '*'
        pattern to match files in output directory. By default all .pb files
        in output/ will be taken.
    files_in_absolute_dir : str, default: None
        if set, pattern will try to match .pb file in this path
        (so remember to add '*' if it's directory)
    create_txt_report : boolean, default: False
        if set to True, will save report as txt file
    """

    files_in_output_dir: str = "*"
    files_in_absolute_dir: str = None
    create_txt_report: bool = False

    def __post_init__(self):
        """Initialize class variables."""
        self.check_scores = False
        self.path_to_all_files = self.set_path_to_files()
        self.counted_votes = defaultdict(int)
        self.counted_scores = defaultdict(int)
        self.filename = None

    def set_path_to_files(self) -> str:
        """Set pattern to .pb files from a given class attribute."""
        if self.files_in_absolute_dir:
            return f"{self.files_in_absolute_dir}.pb"
        return f"{output_path}/{self.files_in_output_dir}.pb"

    def check_output_files(self) -> None:
        """Start checking output files. Trigger needed actions."""
        self.iterate_through_pb_files()
        # print(pb_file)

    def log_different_votes(
        self,
        project_number: str,
        file_votes: int,
        counted_votes: int,
        counted: str = "votes",
    ) -> None:
        """Create text: votes num in PROJECTS differs from counted in VOTES."""

        text = (
            f"Different values in {counted}! "
            f"Project number: {project_number} "
            f"File {counted}: {file_votes} "
            f"vs counted_{counted}: {counted_votes}"
        )
        self.log_and_add_to_report(text)

    def log_exceeded_budget(self, budget: float, budget_spent: float) -> None:
        """Create log text: cost of selected projects exceeded budget."""

        text = (
            f"Cost of selected projects exceeded budget!"
            f"Budget: {budget},"
            f"cost of projects: {budget_spent}"
        )
        self.log_and_add_to_report(text)

    def log_project_exceeded_budget(self, project_data: dict, budget: float) -> None:
        """Create log text: single project exceeded whole budget."""

        text = (
            f"Single project exceeded whole budget! "
            f"Budget available: {int(budget)}, "
            f"project: {project_data['name']} "
            f"cost of project: {project_data['cost']}"
        )

        self.log_and_add_to_report(text)

    def log_exceeded_vote_length(
        self, voter_id: str, max_length: int, voter_votes: int
    ) -> None:
        """Create log text: voter has more votes than allowed."""

        text = (
            f"Vote lenght exceeded! "
            f"Voter ID: {voter_id}, "
            f"max vote length: {max_length}, "
            f"number of voter votes: {voter_votes}"
        )
        self.log_and_add_to_report(text)

    def log_project_with_no_votes(self, project_number):
        """Create log text: project has no votes."""

        text = (
            "Project with no votes! "
            "It's possible, that this project was not approved for voting! "
            f"Project number: {project_number}"
        )
        self.log_and_add_to_report(text)

    def check_if_correct_votes_number(self, projects: dict, votes: dict) -> None:
        """Check if number of votes in PROJECTS is the same as counted.

        Count number of votes from VOTES section (given as dict) and check
        if it's the same as given in PROJECTS.

        Log if there is different number, if there is vote for project which
        is not listed or if project has no votes.
        """

        self.counted_votes = utils.count_votes_per_project(votes)
        for project_number, project_info in projects.items():
            votes = project_info.get("votes", 0) or 0
            if int(votes) == 0:
                self.log_project_with_no_votes(project_number)
            counted_votes = self.counted_votes[project_number]
            if not int(project_info.get("votes", 0) or 0) == int(counted_votes or 0):
                self.log_different_votes(
                    project_number, project_info.get("votes", 0), counted_votes
                )

        for project_number, project_votes in self.counted_votes.items():
            if not projects.get(project_number):
                self.log_different_votes(project_number, 0, project_votes)

            elif "votes" not in projects[project_number]:
                self.log_different_votes(project_number, 0, project_votes)

    def check_if_correct_scores_number(self, projects: dict, votes: dict) -> None:
        """Check if score number given in PROJECTS is the same as counted.

        Count scores per projects and check if it's equal to given number.
        If not, log every project with inconsistent data.
        """

        self.counted_scores = utils.count_points_per_project(votes)
        for project_number, project_info in projects.items():
            counted_votes = self.counted_scores[project_number]
            if not int(project_info.get("score", 0) or 0) == int(counted_votes or 0):
                self.log_different_votes(
                    project_number,
                    project_info.get("score", 0),
                    counted_votes,
                    "score!",
                )

        for project_number, project_votes in self.counted_scores.items():
            if not projects.get(project_number):
                self.log_different_votes(project_number, 0, project_votes, "score")

            elif "votes" not in projects[project_number]:
                self.log_different_votes(project_number, 0, project_votes, "score")

    def remove_last_empty_line(self, filename: str) -> None:
        """If last line of file is empty, remove it."""

        with open(filename) as f_input:
            data = f_input.read().rstrip("\n")
        with open(filename, "w") as f_output:
            f_output.write(data)

    def log_and_add_to_report(self, text: str) -> None:
        """Log given text and add it to report."""

        logger.critical("\n" + text + f" File: {self.filename}")
        text = text.replace("\n", " ")
        text = " ".join(text.split())
        self.report_txt += f"{text}\n"

    def check_number_of_votes(self, meta_votes: str, votes: dict) -> None:
        """Compare number of votes from META and votes and log if not equal."""

        if int(meta_votes) != len(votes):
            text = f"""Different number of votes!
                In meta: {meta_votes}
                vs counted in file (number of rows in VOTES section):
                {str(len(votes))}"""
            self.log_and_add_to_report(text)

    def check_number_of_projects(self, meta_projects: str, projects: dict) -> None:
        """Check if number of projects is the same as in META, log if not."""

        if int(meta_projects) != len(projects):
            text = f"""Different number of projects!
                In meta: {meta_projects}
                vs counted in file (number of rows in PROJECTS section): 
                {str(len(projects))}"""
            self.log_and_add_to_report(text)

    def log_comma_in_float(self, text: str) -> None:
        """Log if there is a comma in float values."""

        logger.critical(
            f"""There is a comma in a float number!
            File: {self.filename}, {text}!"""
        )

    def check_if_commas_in_floats(self, meta: dict, projects: dict):
        """Check if there is a comma in float values."""

        if "," in meta["budget"]:
            self.log_comma_in_float("in budget")
        if meta.get("max_sum_cost"):
            if "," in meta["max_sum_cost"]:
                self.log_comma_in_float("in max_sum_cost")
        for project_number, project_data in projects.items():
            cost = project_data["cost"]
            if not isinstance(cost, int):
                if "," in cost:
                    self.log_comma_in_float(f"in project: {project_number}")

    def run_checks(self, pb_file: str) -> None:
        """Run all checks on a given .pb file."""

        self.filename = os.path.basename(pb_file)
        logger.info(f"Checking file from output: {self.filename}")
        meta, projects, votes, self.check_scores = utils.load_pb_file(pb_file)
        self.check_if_commas_in_floats(meta, projects)
        self.check_budgets(meta, projects)
        self.check_number_of_votes(meta["num_votes"], votes)
        self.check_number_of_projects(meta["num_projects"], projects)
        self.check_if_max_vote_length_exceeded(meta, votes)
        self.check_if_correct_votes_number(projects, votes)
        if self.check_scores:
            self.check_if_correct_scores_number(projects, votes)

    def iterate_through_pb_files(self) -> None:
        """Create list of pb files from a given path and iterate."""

        files = glob.glob(self.path_to_all_files)
        utils.human_sorting(files)
        for pb_file in files:
            self.report_txt = ""
            # self.remove_last_empty_line(pb_file)
            self.run_checks(pb_file)
            if self.create_txt_report:
                self.save_report_to_file()

    def save_report_to_file(self) -> None:
        """Save report with all check comments to a txt file."""

        filename = f"output_check_report_{self.filename}.txt"
        with open(filename, "a+") as f:
            f.write(self.report_txt)
        print(f"Report saved to {filename}")

    def check_if_max_vote_length_exceeded(self, meta: dict, votes: dict) -> None:
        """Check if voter has more votes than allowed."""

        max_length = (
            meta.get("max_length")
            or meta.get("max_length_unit")
            or meta.get("max_length_district")
        )
        if max_length:
            for voter, vote_data in votes.items():
                if len(vote_data["vote"].split(",")) > int(max_length):
                    self.log_exceeded_vote_length(
                        voter, max_length, len(vote_data["vote"].split(","))
                    )

    def check_budgets(self, meta: dict, projects: dict) -> None:
        """Check if budget exceeded or if too expensive project."""

        budget_spent = 0
        budget_available = float(meta["budget"].replace(",", "."))
        all_projects = list()
        for _, project_data in projects.items():
            selected_field = project_data.get("selected")
            if selected_field:
                if int(selected_field) == 1:
                    all_projects.append([_, project_data["cost"], project_data["name"]])
                    budget_spent += int(project_data["cost"])
            if int(project_data["cost"]) > budget_available:
                self.log_project_exceeded_budget(project_data, budget_available)
        if budget_spent > budget_available:
            self.log_exceeded_budget(meta["budget"], budget_spent)
            for project in all_projects:
                print(project)
