import os
import re
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
        self.projects_url = self.preprocess["projects_url"]
        self.additional_funded_project_ids = set(
            self.preprocess.get("additional_funded_project_ids", [])
        )
        self.space_re = re.compile(r"\s+")
        return super().__post_init__()

    def normalize_text(self, text):
        text = str(text or "")
        replacements = {
            "\xa0": " ",
            " ": " ",
            "–": "-",
            "—": "-",
            "„": '"',
            "”": '"',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return self.space_re.sub(" ", text).strip(" ,")

    def match_field(self, text, pattern):
        match = re.search(pattern, text, re.S)
        if not match:
            return ""
        return self.normalize_text(match.group(1))

    def parse_cost(self, text):
        value = (
            str(text)
            .replace("zł", "")
            .replace(" ", "")
            .replace("\xa0", "")
            .replace(",", ".")
            .strip()
        )
        return int(round(float(value)))

    def parse_int(self, text):
        return int(str(text).replace(" ", "").strip())

    def get_source_votes_path(self):
        filename = f"{self.source_votes_excel}.xlsx"
        return os.path.join(
            helper_settings.get_path_to_excel_files(self.unit, self.data_dir), filename
        ).replace("\\", "/")

    def get_output_path(self, filename):
        output_dir = helper_settings.get_path_to_excel_files(
            self.unit, extra_dir=self.data_dir
        )
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{filename}.xlsx").replace("\\", "/")

    def load_votes_source(self):
        votes_df = pd.read_excel(self.get_source_votes_path())
        expected_columns = {
            "IDWPIS",
            "Ile oddanych głosów",
            "WIEK",
            "ID_PROJEKTU",
            "Rodzaj projektu",
            "Numer Rejonu",
            "NAZWA_PROJEKTU",
        }
        missing = expected_columns.difference(votes_df.columns)
        if missing:
            raise RuntimeError(f"Missing Kielce votes columns: {sorted(missing)}")
        return votes_df

    def build_project_district_lookup(self, votes_df):
        project_districts = votes_df.drop_duplicates("ID_PROJEKTU").set_index(
            "ID_PROJEKTU"
        )["Numer Rejonu"]
        return project_districts.to_dict()

    def parse_projects_page(self, project_district_lookup):
        soup = utils.get_soup(self.projects_url)
        projects = []

        for project_card in soup.select("div.budzetobywatelski-prezentacja-projektow-2025"):
            text = project_card.get_text("\n", strip=True)
            project_id = self.match_field(
                text, r"IDENTYFIKATOR ZADANIA:\s*(.*?)\s*(?:NAZWA PROJEKTU:)"
            )
            name = self.match_field(text, r"NAZWA PROJEKTU:\s*(.*?)\s*(?:NR PROJEKTU:)")
            cost = self.parse_cost(
                self.match_field(
                    text, r"KOSZT ZADANIA PO\s+WERYFIKACJI:\s*([\d\s,.]+)\s*zł"
                )
            )
            votes = self.parse_int(
                self.match_field(
                    text,
                    r"LICZBA GŁOSÓW WAŻNYCH ODDANYCH NA PROJEKT:\s*([\d\s]+)",
                )
            )
            selected = int("PROJEKT PRZEZNACZONY DO REALIZACJI" in text)
            if project_id in self.additional_funded_project_ids:
                selected = 2

            try:
                district = project_district_lookup[project_id]
            except KeyError as exc:
                raise RuntimeError(f"Project {project_id} has no vote-source district") from exc
            if district == "-":
                district = "CITYWIDE"

            projects.append(
                {
                    "project_id": project_id,
                    "name": name,
                    "cost": cost,
                    "votes": votes,
                    "district": district,
                    "selected": selected,
                }
            )

        if len(projects) != 85:
            raise RuntimeError(f"Expected 85 Kielce projects, got {len(projects)}")
        return projects

    def validate_vote_totals(self, votes_df, projects):
        counted_votes = votes_df.groupby("ID_PROJEKTU").size().to_dict()
        mismatches = []

        for project in projects:
            project_id = project["project_id"]
            counted = int(counted_votes.get(project_id, 0))
            official = int(project["votes"])
            if counted != official:
                mismatches.append(
                    {
                        "project_id": project_id,
                        "official_votes": official,
                        "counted_votes": counted,
                    }
                )

        if mismatches:
            raise RuntimeError(f"Kielce official/project vote mismatch: {mismatches}")

        source_project_ids = set(counted_votes.keys())
        scraped_project_ids = {project["project_id"] for project in projects}
        if source_project_ids != scraped_project_ids:
            raise RuntimeError(
                "Kielce project ids differ between votes and project page: "
                f"only_votes={sorted(source_project_ids - scraped_project_ids)}, "
                f"only_page={sorted(scraped_project_ids - source_project_ids)}"
            )

    def save_projects(self, projects):
        columns = ["project_id", "name", "cost", "votes", "district", "selected"]
        pd.DataFrame(projects)[columns].to_excel(
            self.get_output_path(self.projects_excel), index=False
        )

    def save_votes(self, votes_df):
        processed_df = pd.DataFrame(
            {
                "voter_id": votes_df["IDWPIS"].astype(int),
                "age": votes_df["WIEK"].astype(int),
                "vote": votes_df["ID_PROJEKTU"],
                "district": votes_df["Numer Rejonu"].replace({"-": "CITYWIDE"}),
                "voting_method": "internet",
            }
        )
        processed_df.to_excel(self.get_output_path(self.votes_excel), index=False)

    def start(self):
        self.logger.info("Running Kielce preprocessing...")
        votes_df = self.load_votes_source()
        project_district_lookup = self.build_project_district_lookup(votes_df)
        projects = self.parse_projects_page(project_district_lookup)
        self.validate_vote_totals(votes_df, projects)
        self.save_projects(projects)
        self.save_votes(votes_df)
        self.logger.info("Kielce preprocessing finished!")
