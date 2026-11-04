import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

import pandas as pd

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    citywide_label = "Projekt ogólnomiejski"
    project_id_pattern = re.compile(r"P\d{4}")
    attendance_bonus_project_ids = {"P0011", "P0029", "P0030", "P0037"}
    voting_method_mapping = {
        "ELECTRONIC": "internet",
        # VoterItem normalizes this Polish source label to Pabulib's `paper`.
        "PAPER": "papier",
    }

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_excel = self.preprocess["source_excel"]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        return super().__post_init__()

    def path(self, filename):
        return utils.get_path_to_file_by_unit(
            filename, self.unit, self.data_dir, ext="xlsx"
        )

    @staticmethod
    def clean_text(value):
        text = str(value).replace("\xa0", " ")
        text = "".join(
            character
            for character in text
            if unicodedata.category(character) != "Cf"
        )
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def clean_cost(value):
        value = round(float(value), 2)
        return int(value) if value.is_integer() else value

    @staticmethod
    def is_true(value):
        return value is True or str(value).strip().lower() == "true"

    def read_source(self):
        path = self.path(self.source_excel)
        return {
            "ballots": pd.read_excel(path, sheet_name="Karty", keep_default_na=False),
            "projects": pd.read_excel(
                path, sheet_name="Projekty", keep_default_na=False
            ),
        }

    def prepare_projects(self, source):
        required_columns = {
            "Lp",
            "Nazwa projektu",
            "Dzielnica",
            "Czy_dopuszczono_do_glosowania",
            "Glosow",
            "Czy_realizacja",
            "Wartosc_do_listy_do_glosowania",
        }
        missing_columns = required_columns.difference(source.columns)
        if missing_columns:
            raise RuntimeError(
                f"Zabrze: missing project columns: {sorted(missing_columns)}"
            )

        admitted = source[
            source["Czy_dopuszczono_do_glosowania"].map(self.is_true)
        ].copy()
        rows = []
        for _, project in admitted.iterrows():
            project_id = self.clean_text(project["Lp"])
            district = self.clean_text(project["Dzielnica"])
            if district == self.citywide_label:
                district = "CITYWIDE"

            selected = int(self.is_true(project["Czy_realizacja"]))
            if selected and project_id in self.attendance_bonus_project_ids:
                selected = 2

            rows.append(
                {
                    "project_id": project_id,
                    "name": self.clean_text(project["Nazwa projektu"]),
                    "cost": self.clean_cost(
                        project["Wartosc_do_listy_do_glosowania"]
                    ),
                    "votes": int(project["Glosow"]),
                    "district": district,
                    "selected": selected,
                }
            )

        projects = pd.DataFrame(rows)
        duplicate_ids = projects[
            projects["project_id"].duplicated(keep=False)
        ]["project_id"].tolist()
        if duplicate_ids:
            raise RuntimeError(
                f"Zabrze: duplicated project ids: {sorted(set(duplicate_ids))}"
            )
        if len(source) != 86 or len(projects) != 67:
            raise RuntimeError(
                "Zabrze: unexpected project totals: "
                f"all={len(source)}, admitted={len(projects)}"
            )
        if int((projects["selected"] > 0).sum()) != 29:
            raise RuntimeError(
                "Zabrze: expected 29 projects selected for implementation"
            )
        actual_bonus_ids = set(
            projects.loc[projects["selected"] == 2, "project_id"].astype(str)
        )
        if actual_bonus_ids != self.attendance_bonus_project_ids:
            raise RuntimeError(
                "Zabrze: unexpected attendance-bonus projects: "
                f"{sorted(actual_bonus_ids)}"
            )
        return projects

    def extract_project_ids(self, value, ballot_id, column):
        text = self.clean_text(value)
        if not text:
            return []
        project_ids = self.project_id_pattern.findall(text)
        if not project_ids:
            raise RuntimeError(
                f"Zabrze: cannot parse {column} on ballot {ballot_id}: {value}"
            )
        if len(project_ids) > 1:
            expected = (
                ballot_id == 20010
                and column == "LOCAL_PROJECT"
                and project_ids == ["P0006", "P0015"]
            )
            if not expected:
                raise RuntimeError(
                    f"Zabrze: unexpected multiple choices on ballot {ballot_id}: "
                    f"{project_ids}"
                )
            self.logger.warning(
                "Zabrze: ballot 20010 contains local projects P0006 and P0015; "
                "both are retained because both are included in the official totals."
            )
        return project_ids

    def prepare_votes(self, source, projects):
        required_columns = {
            "BALLOT_PAPER_NO",
            "KIND",
            "STATE",
            "DISTRICT",
            "CITYWIDE_PROJECT",
            "LOCAL_PROJECT",
        }
        missing_columns = required_columns.difference(source.columns)
        if missing_columns:
            raise RuntimeError(
                f"Zabrze: missing ballot columns: {sorted(missing_columns)}"
            )

        valid = source[source["STATE"].astype(str).str.strip() == "VALID"].copy()
        if len(source) != 22391 or len(valid) != 22391:
            raise RuntimeError(
                "Zabrze: unexpected ballot totals: "
                f"all={len(source)}, valid={len(valid)}"
            )
        if valid["BALLOT_PAPER_NO"].duplicated().any():
            duplicates = valid.loc[
                valid["BALLOT_PAPER_NO"].duplicated(keep=False),
                "BALLOT_PAPER_NO",
            ].tolist()
            raise RuntimeError(
                f"Zabrze: duplicated ballot ids: {sorted(set(duplicates))[:20]}"
            )

        project_district = projects.set_index("project_id")["district"].to_dict()
        rows = []
        empty_ballot_ids = []
        for _, ballot in valid.iterrows():
            ballot_id = int(ballot["BALLOT_PAPER_NO"])
            source_method = self.clean_text(ballot["KIND"]).upper()
            try:
                voting_method = self.voting_method_mapping[source_method]
            except KeyError as exc:
                raise RuntimeError(
                    f"Zabrze: unknown voting method on ballot {ballot_id}: "
                    f"{ballot['KIND']}"
                ) from exc

            neighborhood = self.clean_text(ballot["DISTRICT"])
            ballot_project_count = 0
            for column, expected_pool in (
                ("CITYWIDE_PROJECT", "CITYWIDE"),
                ("LOCAL_PROJECT", "LOCAL"),
            ):
                project_ids = self.extract_project_ids(
                    ballot[column], ballot_id, column
                )
                ballot_project_count += len(project_ids)
                for project_id in project_ids:
                    if project_id not in project_district:
                        raise RuntimeError(
                            f"Zabrze: project {project_id} from ballot {ballot_id} "
                            "is absent from the official results"
                        )
                    district = project_district[project_id]
                    is_citywide = district == "CITYWIDE"
                    if (expected_pool == "CITYWIDE") != is_citywide:
                        raise RuntimeError(
                            f"Zabrze: project {project_id} is in the wrong ballot column"
                        )
                    rows.append(
                        {
                            "voter_id": ballot_id,
                            "vote": project_id,
                            "district": district,
                            "neighborhood": neighborhood,
                            "voting_method": voting_method,
                        }
                    )
            if ballot_project_count == 0:
                empty_ballot_ids.append(ballot_id)

        expected_empty_ballot_ids = [20452, 20795, 21262, 21348, 22229]
        if empty_ballot_ids != expected_empty_ballot_ids:
            raise RuntimeError(
                "Zabrze: unexpected valid ballots without a project choice: "
                f"{empty_ballot_ids}"
            )
        self.logger.info(
            "Zabrze: five valid ballots have no project choice and are not added "
            "to any pool-specific VOTES section."
        )

        votes = pd.DataFrame(rows)
        if len(votes) != 38591:
            raise RuntimeError(
                f"Zabrze: expected 38,591 project indications, got {len(votes)}"
            )

        counted = Counter(votes["vote"].astype(str))
        mismatches = []
        for project in projects.itertuples():
            ballot_count = counted.get(str(project.project_id), 0)
            if ballot_count != int(project.votes):
                mismatches.append(
                    (str(project.project_id), int(project.votes), ballot_count)
                )
        if mismatches:
            raise RuntimeError(
                "Zabrze: official project results differ from ballot counts "
                f"(project_id, official, ballots): {mismatches[:20]}"
            )

        method_counts = Counter(valid["KIND"].astype(str).str.strip())
        expected_method_counts = Counter({"ELECTRONIC": 17993, "PAPER": 4398})
        if method_counts != expected_method_counts:
            raise RuntimeError(
                "Zabrze: unexpected ballot method totals: "
                f"{dict(method_counts)}"
            )
        return votes.sort_values(["voter_id", "district", "vote"]).reset_index(
            drop=True
        )

    def save(self, dataframe, filename):
        dataframe.to_excel(self.path(filename), index=False)

    def start(self):
        self.logger.info("Running Zabrze preprocessing...")
        source = self.read_source()
        projects = self.prepare_projects(source["projects"])
        votes = self.prepare_votes(source["ballots"], projects)
        self.save(projects, self.projects_excel)
        self.save(votes, self.votes_excel)
        self.logger.info("Zabrze preprocessing finished!")
