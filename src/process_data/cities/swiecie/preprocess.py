import os
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction

import pandas as pd
from pypdf import PdfReader

import helpers.settings as helper_settings
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_year = self.preprocess["source_year"]
        self.date_end = datetime.strptime(self.preprocess["date_end"], "%d.%m.%Y")
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        self.budget = 1070000
        return super().__post_init__()

    def get_source_path(self, filename):
        return os.path.join(
            helper_settings.get_path_to_excel_files(self.unit, self.data_dir), filename
        ).replace("\\", "/")

    def get_output_path(self, filename):
        output_dir = helper_settings.get_path_to_excel_files(
            self.unit, extra_dir=self.data_dir
        )
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{filename}.xlsx").replace("\\", "/")

    def normalize(self, text):
        text = str(text or "").replace("\x00", "fi")
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z0-9]+", "", text.lower())

    def normalize_with_index(self, text):
        normalized = []
        index_map = []
        for idx, char in enumerate(str(text or "").replace("\x00", "fi")):
            ascii_char = (
                unicodedata.normalize("NFKD", char).encode("ascii", "ignore").decode()
            )
            for out_char in ascii_char.lower():
                if out_char.isalnum():
                    normalized.append(out_char)
                    index_map.append(idx)
        return "".join(normalized), index_map

    def clean_name(self, text):
        return re.sub(r"\s+", " ", str(text or "").replace("\x00", "fi")).strip()

    def parse_cost(self, text):
        value = (
            str(text)
            .replace("\xa0", "")
            .replace(" ", "")
            .replace(",", ".")
            .strip()
        )
        return int(round(float(value)))

    def parse_pdf(self):
        path = self.get_source_path(f"Wyniki-{self.source_year}.pdf")
        text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        lines = text.splitlines()

        vote_summary = None
        for idx, line in enumerate(lines):
            if line.startswith("WA") and idx + 1 < len(lines):
                values = [int(value) for value in re.findall(r"\d+", lines[idx + 1])]
                if len(values) == 4:
                    vote_summary = {
                        "valid_ballots": values[0],
                        "invalid_ballots": values[1],
                        "valid_indications": values[2],
                        "invalid_indications": values[3],
                    }
                    break
        if vote_summary is None:
            raise RuntimeError(f"Cannot parse Świecie {self.source_year} vote summary")

        projects_part = text.split("Projekty", 1)[1].split("Raport", 1)[0]
        projects = []
        for line in projects_part.splitlines():
            line = line.strip()
            if not re.match(r"^\d+\s+", line):
                continue
            match = re.match(r"^(\d+)\s+(.*?)\s+([\d\s\xa0]+,\d{2})\s*", line)
            if not match:
                raise RuntimeError(f"Cannot parse Świecie project row: {line}")
            public_number, name, cost = match.groups()
            projects.append(
                {
                    "public_number": int(public_number),
                    "pdf_name": self.clean_name(name),
                    "cost": self.parse_cost(cost),
                }
            )

        return vote_summary, projects

    def load_votes_source(self):
        path = self.get_source_path(f"Glosy_{self.source_year}.xlsx")
        votes_df = pd.read_excel(path)
        expected_columns = {"Miasto", "Data urodzenia", "Rodzaj głosu", "Status", "Projekty"}
        missing = expected_columns.difference(votes_df.columns)
        if missing:
            raise RuntimeError(f"Missing Świecie votes columns: {sorted(missing)}")
        return votes_df

    def find_project_name_in_votes(self, project_name, vote_cells):
        project_key = self.normalize(project_name)
        for cell in vote_cells:
            normalized_cell, index_map = self.normalize_with_index(cell)
            start = normalized_cell.find(project_key)
            if start == -1:
                continue
            end = start + len(project_key) - 1
            original_start = index_map[start]
            original_end = index_map[end] + 1
            return str(cell)[original_start:original_end].strip(" ,")
        raise RuntimeError(f"Cannot find project in Świecie votes: {project_name}")

    def build_project_mapping(self, projects, votes_df):
        vote_cells = votes_df["Projekty"].dropna().astype(str).tolist()
        mapping = {}
        processed_projects = []

        for idx, project in enumerate(projects, 1):
            project_id = f"c{idx}"
            vote_name = self.find_project_name_in_votes(project["pdf_name"], vote_cells)
            project_key = self.normalize(project["pdf_name"])
            mapping[project_key] = {
                "project_id": project_id,
                "name": vote_name,
            }
            processed_projects.append(
                {
                    "project_id": project_id,
                    "public_number": project["public_number"],
                    "name": vote_name,
                    "cost": project["cost"],
                    "district": "CITYWIDE",
                    "votes": 0,
                    "selected": 0,
                    "project_key": project_key,
                }
            )

        return mapping, processed_projects

    def detect_projects_in_ballot(self, ballot, projects):
        normalized_ballot = self.normalize(ballot)
        detected = []
        for project in projects:
            position = normalized_ballot.find(project["project_key"])
            if position != -1:
                detected.append((position, project["project_id"]))
        return [project_id for _, project_id in sorted(detected)]

    def process_votes(self, votes_df, projects):
        vote_rows = []
        counts_by_status = {
            "Ważny": defaultdict(int),
            "Nieważny": defaultdict(int),
        }

        valid_voter_number = 0
        for _, row in votes_df.iterrows():
            if row["Status"] == "Ważny":
                valid_voter_number += 1
                voter_id = f"v{valid_voter_number}"
            else:
                voter_id = ""
            detected = self.detect_projects_in_ballot(row["Projekty"], projects)
            if not detected:
                raise RuntimeError(
                    f"Cannot parse Świecie ballot {valid_voter_number}: {row['Projekty']}"
                )
            status = row["Status"]
            if status not in counts_by_status:
                raise RuntimeError(f"Unknown Świecie vote status: {status}")
            age = self.calculate_age(row["Data urodzenia"])
            voting_method = self.normalize_voting_method(row["Rodzaj głosu"])
            for project_id in detected:
                counts_by_status[status][project_id] += 1
                if status == "Ważny":
                    vote_rows.append(
                        {
                            "voter_id": voter_id,
                            "age": age,
                            "district": "CITYWIDE",
                            "neighborhood": row["Miasto"],
                            "vote": project_id,
                            "voting_method": voting_method,
                        }
                    )

        for project in projects:
            project["votes"] = counts_by_status["Ważny"][project["project_id"]]

        return pd.DataFrame(vote_rows), counts_by_status

    def calculate_age(self, birthdate):
        if not hasattr(birthdate, "year"):
            return ""
        age = self.date_end.year - birthdate.year
        if (self.date_end.month, self.date_end.day) < (birthdate.month, birthdate.day):
            age -= 1
        if age < 0 or age > 120:
            return ""
        return age

    def normalize_voting_method(self, voting_method):
        if str(voting_method).lower().startswith("elektronicz"):
            return "internet"
        if str(voting_method).lower().startswith("papier"):
            return "paper"
        raise RuntimeError(f"Unknown Świecie voting method: {voting_method}")

    def validate_summary(self, votes_df, vote_summary, vote_rows, counts_by_status):
        valid_ballots = int((votes_df["Status"] == "Ważny").sum())
        invalid_ballots = int((votes_df["Status"] == "Nieważny").sum())
        valid_indications = sum(counts_by_status["Ważny"].values())
        invalid_indications = sum(counts_by_status["Nieważny"].values())

        actual = {
            "valid_ballots": valid_ballots,
            "invalid_ballots": invalid_ballots,
            "valid_indications": valid_indications,
            "invalid_indications": invalid_indications,
        }
        if actual != vote_summary:
            raise RuntimeError(
                f"Świecie {self.source_year} summary mismatch: "
                f"pdf={vote_summary}, votes={actual}"
            )
        if len(vote_rows) != vote_summary["valid_indications"]:
            raise RuntimeError(
                f"Świecie {self.source_year} valid indication mismatch: "
                f"{len(vote_rows)} != {vote_summary['valid_indications']}"
            )

    def compute_equalshares_fixed_budget(self, projects, approvers, total_budget):
        voters = sorted({voter_id for voter_ids in approvers.values() for voter_id in voter_ids})
        voter_budget = {voter_id: Fraction(total_budget, len(voters)) for voter_id in voters}
        cost = {project["project_id"]: project["cost"] for project in projects}
        remaining = {
            project["project_id"]: len(approvers[project["project_id"]])
            for project in projects
            if project["cost"] > 0 and approvers[project["project_id"]]
        }
        winners = []

        while True:
            best = []
            best_eff_vote_count = Fraction(0, 1)
            for project_id in sorted(remaining, key=lambda item: remaining[item], reverse=True):
                previous_eff_vote_count = remaining[project_id]
                if previous_eff_vote_count < best_eff_vote_count:
                    break

                money_behind_now = sum(
                    voter_budget[voter_id] for voter_id in approvers[project_id]
                )
                if money_behind_now < cost[project_id]:
                    del remaining[project_id]
                    continue

                sorted_approvers = sorted(
                    approvers[project_id], key=lambda voter_id: voter_budget[voter_id]
                )
                paid_so_far = Fraction(0, 1)
                denominator = len(sorted_approvers)

                for voter_id in sorted_approvers:
                    max_payment = Fraction(cost[project_id] - paid_so_far, denominator)
                    eff_vote_count = Fraction(cost[project_id], 1) / max_payment
                    if max_payment > voter_budget[voter_id]:
                        paid_so_far += voter_budget[voter_id]
                        denominator -= 1
                    else:
                        remaining[project_id] = eff_vote_count
                        if eff_vote_count > best_eff_vote_count:
                            best_eff_vote_count = eff_vote_count
                            best = [project_id]
                        elif eff_vote_count == best_eff_vote_count:
                            best.append(project_id)
                        break

            if not best:
                break

            winner = self.break_equalshares_ties(best, projects, approvers)
            winners.append(winner)
            del remaining[winner]

            max_payment = Fraction(cost[winner], 1) / best_eff_vote_count
            for voter_id in approvers[winner]:
                voter_budget[voter_id] = max(
                    Fraction(0, 1), voter_budget[voter_id] - max_payment
                )

        return winners

    def break_equalshares_ties(self, choices, projects, approvers):
        by_id = {project["project_id"]: project for project in projects}
        best_cost = min(by_id[project_id]["cost"] for project_id in choices)
        choices = [
            project_id for project_id in choices if by_id[project_id]["cost"] == best_cost
        ]
        best_approval_count = max(len(approvers[project_id]) for project_id in choices)
        choices = [
            project_id
            for project_id in choices
            if len(approvers[project_id]) == best_approval_count
        ]
        if len(choices) != 1:
            raise RuntimeError(f"Equal Shares tie-breaking failed for projects {choices}")
        return choices[0]

    def compute_selected_projects(self, projects, vote_rows):
        approvers = {
            project["project_id"]: vote_rows[vote_rows["vote"] == project["project_id"]][
                "voter_id"
            ].tolist()
            for project in projects
        }

        winners = self.compute_equalshares_fixed_budget(projects, approvers, self.budget)
        artificial_budget = (self.budget // vote_rows["voter_id"].nunique()) * vote_rows[
            "voter_id"
        ].nunique()

        while True:
            next_budget = artificial_budget + vote_rows["voter_id"].nunique()
            next_winners = self.compute_equalshares_fixed_budget(
                projects, approvers, next_budget
            )
            next_cost = sum(
                project["cost"]
                for project in projects
                if project["project_id"] in next_winners
            )
            if next_cost <= self.budget:
                artificial_budget = next_budget
                winners = next_winners
            else:
                break

        winners = set(winners)
        for project in projects:
            project["selected"] = int(project["project_id"] in winners)

    def save_projects(self, projects):
        columns = ["project_id", "cost", "votes", "name", "district", "selected"]
        pd.DataFrame(projects)[columns].to_excel(
            self.get_output_path(self.projects_excel), index=False
        )

    def save_votes(self, vote_rows):
        vote_rows.to_excel(self.get_output_path(self.votes_excel), index=False)

    def start(self):
        self.logger.info(f"Running Świecie {self.instance} preprocessing...")
        vote_summary, pdf_projects = self.parse_pdf()
        votes_df = self.load_votes_source()
        _, projects = self.build_project_mapping(pdf_projects, votes_df)
        vote_rows, counts_by_status = self.process_votes(votes_df, projects)
        self.validate_summary(votes_df, vote_summary, vote_rows, counts_by_status)
        self.compute_selected_projects(projects, vote_rows)
        self.save_projects(projects)
        self.save_votes(vote_rows)
        self.logger.info(f"Świecie {self.instance} preprocessing finished!")
