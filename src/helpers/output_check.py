import glob
import math
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import List

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
        self.path_to_all_files = self.set_path_to_files()
        self.counted_votes = defaultdict(int)
        self.counted_scores = defaultdict(int)
        self.filename = None
        self.summary = {}

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
        error = f"different values in {counted}"
        self.log_and_add_to_report(error, text)

    def log_exceeded_budget(self, budget: float, budget_spent: float) -> None:
        """Create log text: cost of selected projects exceeded budget."""

        text = (
            f"Cost of selected projects exceeded budget!"
            f"Budget: {budget}, "
            f"cost of projects: {budget_spent}"
        )
        error = "budget exceeded"
        self.log_and_add_to_report(error, text)

    def log_wrong_greedy_winners(self, txt: str) -> None:
        """Create log text: cost of selected projects exceeded budget."""

        text = f"Wrong selected projects if Greedy rule applied! " f"{txt}"
        error = "greedy rule not followed"
        self.log_and_add_to_report(error, text)

    def log_wrong_poznan_winners(self, txt: str) -> None:
        """Create log text: cost of selected projects exceeded budget."""

        text = f"Wrong selected projects if Poznań rule applied! " f"{txt}"
        error = "poznan rule not followed"
        self.log_and_add_to_report(error, text)

    def log_greedy_difference(
        self, greedy: dict, selected: dict, rule="GREEDY"
    ) -> None:
        """Create log text: cost of selected projects exceeded budget."""

        text = ""
        if selected:
            text += "PROJECTS SELECTED IN FILE:\n"

            for project in selected.values():
                text += f"{str(project)}\n"

        if greedy:
            text += f"PROJECTS THAT SHOULD BE SELECTED IN {rule} RULE:\n"

            for project in greedy.values():
                text += f"{str(project)}\n"

        logger.critical("\n" + text + f" File: {self.filename}")

    def log_all_projects_funded(self, budget: float, all_projects_cost: float) -> None:
        """Create log text: cost of selected projects exceeded budget."""

        text = (
            f"Budget is higher than cost of all projects! "
            "Voting made no sense, all projets were funded. "
            f"Budget: {utils.get_str_with_sep_from(budget)}, "
            "cost of all projects: "
            f"{utils.get_str_with_sep_from(all_projects_cost)}"
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

        error = "single project exceeded whole budget"
        self.log_and_add_to_report(error, text)

    def log_project_no_cost(self, project_data: dict) -> None:
        """Create log text: single project exceeded whole budget."""

        text = (
            f"There is project with no cost! "
            f"It's possible that it was not approved for voting! "
            f"project: {project_data['name']} "
        )

        error = "project with no cost"
        self.log_and_add_to_report(error, text)

    def log_exceeded_vote_length(
        self, voter_id: str, max_length: int, voter_votes: int
    ) -> None:
        """Create log text: voter has more votes than allowed."""

        text = (
            f"Vote length exceeded! "
            f"Voter ID: {voter_id}, "
            f"max vote length: {max_length}, "
            f"number of voter votes: {voter_votes}"
        )

        error = "vote length exceeded"
        self.log_and_add_to_report(error, text)

    def log_duplicated_votes(self, voter_id: str, votes: List[int]) -> None:
        """Create log text: voter has duplicated votes."""

        text = (
            f"Duplicated projects in Voter's vote! "
            f"Voter ID: {voter_id}, "
            f"vote: {votes}, "
            f"should be: {set(votes)}"
        )

        error = "vote with duplicated projects"
        self.log_and_add_to_report(error, text)

    def log_too_short_vote_length(
        self, voter_id: str, min_length: int, voter_votes: int
    ) -> None:
        """Create log text: voter has more votes than allowed."""

        text = (
            f"Vote length is too short! "
            f"Voter ID: {voter_id}, "
            f"min vote length: {min_length}, "
            f"number of voter votes: {voter_votes}"
        )
        error = "vote length too short"
        self.log_and_add_to_report(error, text)

    def log_project_with_no_votes(self, project_number):
        """Create log text: project has no votes."""

        text = (
            "Project with no votes! "
            "It's possible, that this project was not approved for voting! "
            f"Project number: {project_number}"
        )
        error = "project with no votes"
        self.log_and_add_to_report(error, text)

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
                    "score",
                )

        for project_number, project_votes in self.counted_scores.items():
            if not projects.get(project_number):
                self.log_different_votes(project_number, 0, project_votes, "score")

    def remove_last_empty_line(self, filename: str) -> None:
        """If last line of file is empty, remove it."""

        with open(filename) as f_input:
            data = f_input.read().rstrip("\n")
        with open(filename, "w") as f_output:
            f_output.write(data)

    def log_and_add_to_report(self, error, text: str) -> None:
        """Log given text and add it to report."""
        logger.critical("\n" + text + f" File: {self.filename}")
        text = text.replace("\n", " ")
        text = " ".join(text.split())
        self.summary[error] = self.summary.get(error, 0) + 1
        self.report_txt += f"{text}\n"

    def check_number_of_votes(self, meta_votes: str, votes: dict) -> None:
        """Compare number of votes from META and votes and log if not equal."""

        if int(meta_votes) != len(votes):
            text = f"""Different number of votes!
                In meta: {meta_votes}
                vs counted in file (number of rows in VOTES section):
                {str(len(votes))}"""
            error = "different number of votes"
            self.log_and_add_to_report(error, text)

    def check_number_of_projects(self, meta_projects: str, projects: dict) -> None:
        """Check if number of projects is the same as in META, log if not."""

        if int(meta_projects) != len(projects):
            text = (
                f"Different number of projects! "
                f"In meta: {meta_projects} "
                f"vs counted in file (number of rows in PROJECTS section): "
                f"{str(len(projects))}"
            )
            error = "different number of projects"
            self.log_and_add_to_report(error, text)

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
        (meta, projects, votes, self.check_votes, self.check_scores) = (
            utils.load_pb_file(pb_file)
        )
        self.check_if_commas_in_floats(meta, projects)
        self.check_budgets(meta, projects)
        self.check_number_of_votes(meta["num_votes"], votes)
        self.check_number_of_projects(meta["num_projects"], projects)
        self.check_vote_length(meta, votes)
        self.check_votes_and_scores(projects, votes)
        self.verify_selected(meta, projects)
        country = meta["country"]
        unit = meta["unit"]
        instance = meta["instance"]
        webpage_name = f"{country} {unit} {instance}"
        if meta.get("subunit"):
            webpage_name += f" {meta['subunit']}"
        logger.info(f"PB name would be created on webpage: `{webpage_name}`")

    def check_votes_and_scores(self, projects, votes):
        if not any([self.check_votes, self.check_scores]):
            logger.info("There are no votes counted in PROJECTS section!")
            error_text = "No votes counted in PROJECTS section"
            self.summary[error_text] = self.summary.get(error_text, 0) + 1
        else:
            if self.check_votes:
                self.check_if_correct_votes_number(projects, votes)
            if self.check_scores:
                self.check_if_correct_scores_number(projects, votes)

    def verify_selected(self, meta, projects):
        selected_field = next(iter(projects.values())).get("selected")
        if selected_field:
            projects = utils.sort_projects_by_results(projects)
            results = "votes"
            if self.check_scores:
                results = "score"
            budget = float(meta["budget"].replace(",", "."))
            if meta["unit"] == "Poznań":
                self.verify_poznan_selected(budget, projects, results)
            else:
                self.verify_greedy_selected(budget, projects, results)
        else:
            logger.info("There is no selected field!")
            error_text = "No selected field in PROJECTS section"
            self.summary[error_text] = self.summary.get(error_text, 0) + 1

    def print_summary(self):
        summary_sorted = dict(
            sorted(self.summary.items(), key=lambda x: x[1], reverse=True)
        )

        summary_text = (
            "\n**********************************************\n"
            "SUMMARY"
            "\n**********************************************"
        )

        for error_text, value in summary_sorted.items():
            value = f"{value:04}"
            value = value.replace("0", " ", len(value) - len(value.lstrip("0")))
            summary_text += f"\n{value} || {error_text}"

        summary_text += "\n**********************************************"
        logger.critical(summary_text)

    def verify_poznan_selected(self, budget, projects, results):
        file_selected = dict()
        rule_selected = dict()
        get_rule_projects = True
        for project_id, project_dict in projects.items():
            project_cost = float(project_dict["cost"])
            cost_printable = utils.make_cost_printable(project_cost)
            row = [project_id, project_dict[results], cost_printable]
            if int(project_dict["selected"]) in (1, 2):
                # 2 for projects from 80% rule
                file_selected[project_id] = row
            if get_rule_projects:
                if budget >= project_cost:
                    rule_selected[project_id] = row
                    budget -= project_cost
                else:
                    if budget >= project_cost * 0.8:
                        # if there is no more budget but project costs
                        # 80% of left budget it would be funded
                        rule_selected[project_id] = row
                    get_rule_projects = False
        rule_selected_set = set(rule_selected.keys())
        file_selected_set = set(file_selected.keys())
        should_be_selected = rule_selected_set.difference(file_selected_set)
        if should_be_selected:
            text = f"Projects not selected but should be: {should_be_selected}"
            self.log_wrong_poznan_winners(text)

        shouldnt_be_selected = file_selected_set.difference(rule_selected_set)
        if shouldnt_be_selected:
            text = f"Projects selected but should not: {shouldnt_be_selected}"
            self.log_wrong_poznan_winners(text)

        if should_be_selected or should_be_selected:
            self.log_greedy_difference(rule_selected, file_selected, "POZNAŃ")

    def verify_greedy_selected(self, budget, projects, results):
        selected_projects = dict()
        greedy_winners = dict()
        for project_id, project_dict in projects.items():
            project_cost = float(project_dict["cost"])
            cost_printable = utils.make_cost_printable(project_cost)
            row = [project_id, project_dict[results], cost_printable]
            if int(project_dict["selected"]) == 1:
                selected_projects[project_id] = row
            if budget >= project_cost:
                greedy_winners[project_id] = row
                budget -= project_cost
        gw_set = set(greedy_winners.keys())
        selected_set = set(selected_projects.keys())
        should_be_selected = gw_set.difference(selected_set)
        if should_be_selected:
            text = f"Projects not selected but should be: {should_be_selected}"
            self.log_wrong_greedy_winners(text)

        shouldnt_be_selected = selected_set.difference(gw_set)
        if shouldnt_be_selected:
            text = f"Projects selected but should not: {shouldnt_be_selected}"
            self.log_wrong_greedy_winners(text)

        if should_be_selected or should_be_selected:
            self.log_greedy_difference(greedy_winners, selected_projects)

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

        if self.summary:
            self.print_summary()

    def save_report_to_file(self) -> None:
        """Save report with all check comments to a txt file."""

        filename = f"output_check_report_{self.filename}.txt"
        with open(filename, "a+") as f:
            f.write(self.report_txt)
        print(f"Report saved to {filename}")

    def check_vote_length(self, meta: dict, votes: dict) -> None:
        """Check if voter has more or less votes than allowed."""

        max_length = (
            meta.get("max_length")
            or meta.get("max_length_unit")
            or meta.get("max_length_district")
        )

        min_length = (
            meta.get("min_length")
            or meta.get("min_length_unit")
            or meta.get("min_length_district")
        )
        check_length = max_length or min_length or None

        if check_length:
            for voter, vote_data in votes.items():
                votes = vote_data["vote"].split(",")
                if len(votes) > len(set(votes)):
                    self.log_duplicated_votes(voter, votes)
                if max_length:
                    if len(votes) > int(max_length):
                        self.log_exceeded_vote_length(voter, max_length, len(votes))
                if min_length:
                    if len(votes) < int(min_length):
                        self.log_too_short_vote_length(voter, min_length, len(votes))

    def check_budgets(self, meta: dict, projects: dict) -> None:
        """Check if budget exceeded or if too expensive project."""

        budget_spent = 0
        all_projects_cost = 0
        budget_available = math.floor(float(meta["budget"].replace(",", ".")))
        all_projects = list()
        for _, project_data in projects.items():
            selected_field = project_data.get("selected")
            project_cost = int(project_data["cost"])
            all_projects_cost += project_cost
            if selected_field:
                if int(selected_field) == 1:
                    all_projects.append([_, project_cost, project_data["name"]])
                    budget_spent += project_cost
            if project_cost == 0:
                self.log_project_no_cost(project_data)
            elif project_cost > budget_available:
                self.log_project_exceeded_budget(project_data, budget_available)
        if budget_spent > budget_available:
            self.log_exceeded_budget(budget_available, budget_spent)
            for project in all_projects:
                print(project)
        if budget_available > all_projects_cost:
            self.log_all_projects_funded(budget_available, all_projects_cost)
