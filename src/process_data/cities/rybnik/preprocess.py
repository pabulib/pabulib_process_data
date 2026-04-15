import os
import re
import ssl
import urllib.request
from dataclasses import dataclass

import pandas as pd
from bs4 import BeautifulSoup

import helpers.settings as helper_settings
import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_votes_excel = self.preprocess["source_votes_excel"]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        self.results_url = self.preprocess["results_url"]
        self.space_re = re.compile(r"\s+")
        self.ballot_split_re = re.compile(r",\s*\n(?=Nr\s+\d+\.)")
        self.ballot_entry_re = re.compile(r"^Nr\s+(\d+)\.\s*(.*)$", re.S)
        return super().__post_init__()

    def fetch_html(self, url):
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, context=context) as response:
            return response.read().decode("utf-8")

    def normalize_text(self, text):
        text = str(text or "")
        replacements = {
            "\xa0": " ",
            " ": " ",
            "–": "-",
            "—": "-",
            "„": '"',
            "”": '"',
            "’": "'",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return self.space_re.sub(" ", text).strip(" ,")

    def normalize_selected(self, status):
        status = self.normalize_text(status).lower()
        if status == "wybrany do realizacji":
            return "wybrane"
        return "niewybrane"

    def parse_cost(self, text):
        text = (
            str(text or "")
            .replace("Koszt:", "")
            .replace("zł", "")
            .replace("PLN", "")
            .replace("\xa0", "")
            .replace(" ", "")
            .replace(" ", "")
            .replace(",", ".")
            .strip()
        )
        return int(round(float(text)))

    def parse_results_page(self):
        html = self.fetch_html(self.results_url)
        soup = BeautifulSoup(html, "html.parser")
        projects = []

        citywide_wrapper = soup.select_one("#results-tab .results-types-section-wrapper")
        for row in citywide_wrapper.select(".result-row"):
            projects.append(self.parse_project_row(row, "CITYWIDE"))

        for wrapper in soup.select(".results-quarter-wrapper"):
            header = wrapper.select_one(".results-header-title").get_text(" ", strip=True)
            district = header.split(" Oddanych głosów:")[0].strip()
            for row in wrapper.select(".result-row"):
                projects.append(self.parse_project_row(row, district))

        if len(projects) != 44:
            raise RuntimeError(f"Expected 44 projects on results page, got {len(projects)}")
        return projects

    def parse_project_row(self, row, district):
        public_number = int(
            row.select_one(".project_nr").get_text(" ", strip=True).replace(".", "")
        )
        name = self.normalize_text(
            row.select_one(".project-name-wrapper").find_all("span")[-1].get_text(
                " ", strip=True
            )
        )
        votes = int(re.sub(r"\D", "", row.select_one(".td-inner.votes").get_text()))
        cost = self.parse_cost(row.select_one(".td-inner.price").get_text(" ", strip=True))
        status = row.select(".status")[-1].get_text(" ", strip=True)
        return {
            "project_id": int(row["data-project-id"]),
            "public_number": public_number,
            "name": name,
            "cost": cost,
            "votes": votes,
            "district": district,
            "selected": self.normalize_selected(status),
            "results_status": self.normalize_text(status),
            "project_url": row.select_one("a.btn")["href"],
        }

    def get_source_votes_path(self):
        filename = f"{self.source_votes_excel}.xlsx"
        return os.path.join(
            helper_settings.get_path_to_excel_files(self.unit), filename
        ).replace("\\", "/")

    def get_output_path(self, filename):
        output_dir = helper_settings.get_path_to_excel_files(self.unit, extra_dir=self.data_dir)
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{filename}.xlsx").replace("\\", "/")

    def save_projects(self, projects):
        columns = [
            "project_id",
            "public_number",
            "name",
            "cost",
            "votes",
            "district",
            "selected",
            "results_status",
            "project_url",
        ]
        df = pd.DataFrame(projects)[columns]
        df.to_excel(self.get_output_path(self.projects_excel), index=False)

    def split_ballot_projects(self, text):
        text = str(text or "").strip()
        if not text:
            return []

        entries = []
        for part in self.ballot_split_re.split(text):
            match = self.ballot_entry_re.match(part.strip())
            if not match:
                raise RuntimeError(f"Cannot parse ballot entry: {part}")
            public_number, title = match.groups()
            entries.append((int(public_number), self.normalize_text(title)))
        return entries

    def build_vote_lookup(self, projects):
        lookup = {}
        for project in projects:
            key = (project["public_number"], self.normalize_text(project["name"]))
            lookup[key] = project
        return lookup

    def process_votes(self, projects):
        votes_df = pd.read_excel(self.get_source_votes_path())
        vote_lookup = self.build_vote_lookup(projects)
        processed_rows = []

        for _, row in votes_df.iterrows():
            if row["Status"] != "Ważny":
                continue

            voter_id = int(row["Nr głosu"])
            voting_method = self.normalize_text(row["Typ głosu"]).lower()
            age = int(row["Wiek w latach wyliczony na ostatni dzień głosowania"])
            sex = self.normalize_text(row["Płeć"])

            ballot_projects = self.split_ballot_projects(row["Nr projektów"])
            for public_number, title in ballot_projects:
                try:
                    project = vote_lookup[(public_number, title)]
                except KeyError as exc:
                    raise RuntimeError(
                        f"Unknown ballot project: {public_number} | {title}"
                    ) from exc

                processed_rows.append(
                    {
                        "voter_id": voter_id,
                        "age": age,
                        "sex": sex,
                        "voting_method": voting_method,
                        "district": project["district"],
                        "vote": str(project["project_id"]),
                    }
                )

        processed_df = pd.DataFrame(processed_rows)
        self.validate_vote_totals(processed_df, projects)
        processed_df.to_excel(self.get_output_path(self.votes_excel), index=False)

    def validate_vote_totals(self, processed_df, projects):
        counted_votes = {
            int(project_id): count
            for project_id, count in processed_df.groupby("vote")["voter_id"]
            .nunique()
            .to_dict()
            .items()
        }
        mismatches = []
        for project in projects:
            project_id = int(project["project_id"])
            official_votes = int(project["votes"])
            counted = counted_votes.get(project_id, 0)
            if counted != official_votes:
                mismatches.append(
                    {
                        "project_id": project_id,
                        "name": project["name"],
                        "official_votes": official_votes,
                        "counted_votes": counted,
                    }
                )

        if mismatches:
            raise RuntimeError(f"Rybnik votes mismatch: {mismatches}")

    def start(self):
        self.logger.info("Running Rybnik preprocessing...")
        projects = self.parse_results_page()
        self.save_projects(projects)
        self.process_votes(projects)
