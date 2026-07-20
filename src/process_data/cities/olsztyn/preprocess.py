import re
from collections import Counter
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    vote_pattern = re.compile(r"^\s*Nr\s+(\d+)\.\s", re.IGNORECASE | re.MULTILINE)
    valid_status = "ważny"

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_votes_excel = self.preprocess["source_votes_excel"]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        self.results_url = self.preprocess["results_url"]
        return super().__post_init__()

    def source_path(self, filename):
        return utils.get_path_to_file_by_unit(
            filename, self.unit, self.data_dir, ext="xlsx"
        )

    def fetch_results(self):
        response = requests.get(self.results_url, timeout=30)
        response.raise_for_status()
        return response.text

    @staticmethod
    def parse_int(element):
        digits = re.sub(r"\D", "", element.get_text(" ", strip=True))
        if not digits:
            raise RuntimeError(f"Olsztyn: cannot parse an integer from {element}")
        return int(digits)

    def parse_projects(self, html):
        soup = BeautifulSoup(html, "html.parser")
        projects = []

        for section in soup.select(".results-types-section-wrapper"):
            type_element = section.select_one(".projects_type_label .semi-bold")
            if type_element is None:
                continue
            project_type = type_element.get_text(" ", strip=True).lower()

            for row in section.select(".result-row"):
                number_element = row.select_one(".project_nr")
                name_element = row.select_one(".project-name-wrapper")
                votes_element = row.select_one(".td-inner.votes")
                cost_element = row.select_one(".td-inner.price")
                link_element = row.select_one(".project-name a[href]")
                if not all(
                    (number_element, name_element, votes_element, cost_element, link_element)
                ):
                    raise RuntimeError("Olsztyn: incomplete project row on results page")

                project_id = number_element.get_text(strip=True).rstrip(".")
                name = name_element.get_text(" ", strip=True)
                name = re.sub(rf"^{re.escape(project_id)}\.\s*", "", name)

                quarter = row.find_parent(class_="results-quarter-wrapper")
                if project_type == "miejskie":
                    district = "CITYWIDE"
                elif quarter is not None:
                    header = quarter.select_one(".results-header-title")
                    district = next(header.stripped_strings)
                else:
                    raise RuntimeError(
                        f"Olsztyn: missing district for local project {project_id}"
                    )

                projects.append(
                    {
                        "project_id": project_id,
                        "name": name,
                        "cost": self.parse_int(cost_element),
                        "votes": self.parse_int(votes_element),
                        "district": district,
                        "selected": int("win" in row.get("class", [])),
                        "project_url": link_element["href"],
                    }
                )

        project_ids = [project["project_id"] for project in projects]
        if len(projects) != 75 or len(set(project_ids)) != 75:
            raise RuntimeError(
                "Olsztyn: expected 75 unique projects on the results page, "
                f"got {len(projects)} rows and {len(set(project_ids))} ids"
            )
        return pd.DataFrame(projects)

    def parse_votes(self, projects_df):
        source = pd.read_excel(self.source_path(self.source_votes_excel))
        required_columns = {
            "Lp.",
            "Typ głosu",
            "Status",
            "Nr projektów",
            "Płeć",
        }
        missing_columns = required_columns.difference(source.columns)
        if missing_columns:
            raise RuntimeError(
                f"Olsztyn: missing vote columns: {sorted(missing_columns)}"
            )

        valid = source[
            source["Status"].astype(str).str.strip().str.lower() == self.valid_status
        ]
        project_district = projects_df.set_index("project_id")["district"].to_dict()
        rows = []

        for _, ballot in valid.iterrows():
            project_ids = self.vote_pattern.findall(str(ballot["Nr projektów"]))
            if not project_ids:
                raise RuntimeError(
                    f"Olsztyn: no project number found on ballot {ballot['Lp.']}"
                )
            if len(project_ids) != len(set(project_ids)):
                raise RuntimeError(
                    f"Olsztyn: duplicate project on ballot {ballot['Lp.']}"
                )

            for project_id in project_ids:
                if project_id not in project_district:
                    raise RuntimeError(
                        f"Olsztyn: project {project_id} from ballot "
                        f"{ballot['Lp.']} is absent from official results"
                    )
                rows.append(
                    {
                        "voter_id": int(ballot["Lp."]),
                        "sex": ballot["Płeć"],
                        "vote": project_id,
                        "district": project_district[project_id],
                        "voting_method": ballot["Typ głosu"],
                    }
                )

        votes_df = pd.DataFrame(rows)
        if len(valid) != 10502 or len(votes_df) != 49187:
            raise RuntimeError(
                "Olsztyn: unexpected ballot totals: "
                f"valid={len(valid)}, indications={len(votes_df)}"
            )
        return votes_df

    @staticmethod
    def validate_vote_totals(projects_df, votes_df):
        counted = Counter(votes_df["vote"].astype(str))
        mismatches = []
        for project in projects_df.itertuples():
            actual = counted.get(str(project.project_id), 0)
            if actual != int(project.votes):
                mismatches.append((str(project.project_id), int(project.votes), actual))
        if mismatches:
            raise RuntimeError(
                "Olsztyn: official results differ from ballot counts "
                f"(project_id, official, ballots): {mismatches[:20]}"
            )

    def save(self, dataframe, filename):
        path = self.source_path(filename)
        dataframe.to_excel(path, index=False)

    def start(self):
        self.logger.info("Running Olsztyn preprocessing...")
        projects_df = self.parse_projects(self.fetch_results())
        votes_df = self.parse_votes(projects_df)
        self.validate_vote_totals(projects_df, votes_df)
        self.save(projects_df, self.projects_excel)
        self.save(votes_df, self.votes_excel)
        self.logger.info("Olsztyn preprocessing finished!")

