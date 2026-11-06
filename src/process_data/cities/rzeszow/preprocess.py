import os
import re
from dataclasses import dataclass

import pandas as pd

import helpers.settings as helper_settings
from process_data.base_config import BaseConfig


PROJECTS_MISSING_FROM_RESULTS = [
    {
        "project_id": "36",
        "name": "Konserwacja i wyeksponowanie jupitera ze stadionu Stali Rzeszów",
        "district": "GENERAŁA GROTA ROWECKIEGO",
        "neighborhood": "GENERAŁA GROTA ROWECKIEGO",
        "category": "Kategoria II",
        "source_district": "GENERAŁA GROTA ROWECKIEGO",
        "cost": 400000,
        "votes": 94,
        "selected": 0,
    }
]

NEIGHBORHOOD_DISPLAY_NAMES = {
    "1000-LECIA": "1000-Lecia",
    "BARANÓWKA": "Baranówka",
    "BIAŁA": "Biała",
    "BUDZIWÓJ": "Budziwój",
    "BZIANKA": "Bzianka",
    "DRABINIANKA": "Drabinianka",
    "DĄBROWSKIEGO": "Dąbrowskiego",
    "GENERAŁA GROTA ROWECKIEGO": "Generała Grota Roweckiego",
    "GENERAŁA WŁADYSŁAWA ANDERSA": "Generała Władysława Andersa",
    "KMITY": "Kmity",
    "KOTULI": "Kotuli",
    "KRAKOWSKA-POŁUDNIE": "Krakowska-Południe",
    "KRÓLA STANISŁAWA AUGUSTA": "Króla Stanisława Augusta",
    "MATYSÓWKA": "Matysówka",
    "MIESZKA I": "Mieszka I",
    "MIŁOCIN": "Miłocin",
    "MIŁOCIN - ŚW. HUBERTA": "Miłocin - Św. Huberta",
    "NOWE MIASTO": "Nowe Miasto",
    "OGÓLNOMIEJSKI": "Citywide",
    "PADEREWSKIEGO": "Paderewskiego",
    "PIASTÓW": "Piastów",
    "POBITNO": "Pobitno",
    "POGWIZDÓW NOWY": "Pogwizdów Nowy",
    "PRZYBYSZÓWKA": "Przybyszówka",
    "PUŁASKIEGO": "Pułaskiego",
    "STAROMIEŚCIE": "Staromieście",
    "STARONIWA": "Staroniwa",
    "SŁOCINA": "Słocina",
    "WILKOWYJA": "Wilkowyja",
    "ZALESIE": "Zalesie",
    "ZAWISZY CZARNEGO": "Zawiszy Czarnego",
    "ZAŁĘŻE": "Załęże",
    "ZWIĘCZYCA": "Zwięczyca",
    "ŚRÓDMIEŚCIE": "Śródmieście",
}


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_projects_excel = self.preprocess["source_projects_excel"]
        self.source_votes_excel = self.preprocess["source_votes_excel"]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        self.accepted_project_ids = set(self.preprocess["accepted_project_ids"])
        self.source_schema = self.preprocess.get("source_schema", "rbo_2026")
        self.expected_projects = self.preprocess.get("expected_projects", 161)
        self.votes_column = self.preprocess.get("votes_column", "Oddane głosy")
        self.prefix_voter_ids_by_method = self.preprocess.get(
            "prefix_voter_ids_by_method", False
        )
        self.enforce_one_per_category = self.preprocess.get(
            "enforce_one_per_category", False
        )
        self.project_totals_output_source = self.preprocess.get(
            "project_totals_output_source", "official_projects_results"
        )
        self.expected_valid_ballots = self.preprocess.get("expected_valid_ballots")
        self.expected_valid_indications = self.preprocess.get(
            "expected_valid_indications"
        )
        return super().__post_init__()

    def get_source_path(self, filename):
        return os.path.join(
            helper_settings.get_path_to_excel_files(self.unit, self.data_dir),
            f"{filename}.xlsx",
        ).replace("\\", "/")

    def get_output_path(self, filename):
        output_dir = helper_settings.get_path_to_excel_files(
            self.unit, extra_dir=self.data_dir
        )
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{filename}.xlsx").replace("\\", "/")

    def normalize_category(self, category):
        if category == "KATEGORIA I":
            return "Kategoria I"
        if category == "KATEGORIA II":
            return "Kategoria II"
        if category == "KATEGORIA III":
            return "Kategoria III"
        return category

    def normalize_neighborhood(self, neighborhood):
        neighborhood = str(neighborhood).strip()
        return NEIGHBORHOOD_DISPLAY_NAMES.get(neighborhood, neighborhood.title())

    @staticmethod
    def parse_int(value):
        if isinstance(value, (int, float)) and pd.notna(value):
            return int(value)
        digits = re.sub(r"\D", "", str(value))
        if not digits:
            raise RuntimeError(f"Cannot parse an integer from: {value!r}")
        return int(digits)

    @staticmethod
    def normalize_card_number(value):
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value).strip()

    def load_projects(self):
        raw_df = pd.read_excel(self.get_source_path(self.source_projects_excel), header=None)
        projects = []
        project_pool = {}
        project_neighborhood = {}
        project_category = {}
        current_category = None

        for _, row in raw_df.iterrows():
            first_cell = row.iloc[0]
            if isinstance(first_cell, str) and first_cell.startswith("KATEGORIA"):
                current_category = first_cell.strip()
                continue

            if not pd.notna(first_cell) or not isinstance(first_cell, (int, float)):
                continue

            if self.source_schema == "rbo_2027":
                project_id = self.parse_int(row.iloc[1])
                name = row.iloc[2]
                neighborhood = str(row.iloc[3]).strip()
                cost = self.parse_int(row.iloc[4])
                official_votes = self.parse_int(row.iloc[6])
            else:
                project_id = int(first_cell)
                name = row.iloc[1]
                neighborhood = str(row.iloc[2]).strip()
                cost = int(row.iloc[3])
                official_votes = int(row.iloc[5])

            if current_category is None:
                raise RuntimeError(
                    f"Missing Rzeszów category for project {project_id}"
                )
            neighborhood_display = self.normalize_neighborhood(neighborhood)
            if current_category == "KATEGORIA II":
                pool = neighborhood
            else:
                pool = self.normalize_category(current_category)
            if project_id in project_pool:
                raise RuntimeError(f"Duplicated Rzeszów project ID: {project_id}")
            project_pool[project_id] = pool
            project_neighborhood[project_id] = neighborhood_display
            project_category[project_id] = self.normalize_category(current_category)
            projects.append(
                {
                    "project_id": str(project_id),
                    "name": name,
                    "district": pool,
                    "neighborhood": neighborhood_display,
                    "category": self.normalize_category(current_category),
                    "source_district": neighborhood,
                    "cost": cost,
                    "votes": official_votes,
                    "selected": int(project_id in self.accepted_project_ids),
                }
            )

        if self.source_schema == "rbo_2026":
            for project in PROJECTS_MISSING_FROM_RESULTS:
                project_id = int(project["project_id"])
                if project_id not in project_pool:
                    projects.append(project)
                    project_pool[project_id] = project["district"]
                    project_neighborhood[project_id] = self.normalize_neighborhood(
                        project["source_district"]
                    )
                    project_category[project_id] = project["category"]

        if len(projects) != self.expected_projects:
            raise RuntimeError(
                f"Expected {self.expected_projects} Rzeszów projects, "
                f"got {len(projects)}"
            )

        return (
            pd.DataFrame(projects),
            project_pool,
            project_neighborhood,
            project_category,
        )

    def normalize_voting_method(self, value):
        value = str(value).strip().lower()
        if value.startswith("elektronicz"):
            return "internet"
        if value.startswith("papier"):
            return "papier"
        raise RuntimeError(f"Unknown Rzeszów voting method: {value}")

    def build_voter_ids(self, votes_df):
        if not self.prefix_voter_ids_by_method:
            return votes_df["Nr karty"].map(int)

        methods = votes_df["Wersja"].map(self.normalize_voting_method)
        card_numbers = votes_df["Nr karty"].map(self.normalize_card_number)
        keys = pd.DataFrame({"method": methods, "card": card_numbers})
        occurrences = keys.groupby(["method", "card"], sort=False).cumcount() + 1
        group_sizes = keys.groupby(["method", "card"], sort=False)[
            "card"
        ].transform("size")

        voter_ids = []
        for method, card, occurrence, group_size in zip(
            methods, card_numbers, occurrences, group_sizes
        ):
            method_prefix = "i" if method == "internet" else "p"
            suffix = f"-{occurrence}" if group_size > 1 else ""
            voter_ids.append(f"{method_prefix}-{card}{suffix}")
        return pd.Series(voter_ids, index=votes_df.index)

    def load_votes(self, project_pool, project_neighborhood, project_category):
        votes_df = pd.read_excel(self.get_source_path(self.source_votes_excel), header=1)
        required_columns = {
            "Nr karty",
            "Wersja",
            self.votes_column,
            "Ważność karty",
        }
        missing_columns = required_columns.difference(votes_df.columns)
        if missing_columns:
            raise RuntimeError(
                f"Missing Rzeszów vote columns: {sorted(missing_columns)}"
            )
        votes_df = votes_df.copy()
        votes_df["_voter_id"] = self.build_voter_ids(votes_df)
        valid_votes = votes_df[votes_df["Ważność karty"] == "WAŻNA"]
        processed_rows = []
        skipped_project_ids = {}

        for _, row in valid_votes.iterrows():
            voter_id = row["_voter_id"]
            voting_method = self.normalize_voting_method(row["Wersja"])
            ballot_project_ids = []
            for raw_project_id in str(row[self.votes_column]).split(";"):
                raw_project_id = raw_project_id.strip()
                if not raw_project_id:
                    continue
                project_id = int(raw_project_id)
                ballot_project_ids.append(project_id)

            if len(ballot_project_ids) != len(set(ballot_project_ids)):
                raise RuntimeError(
                    f"Rzeszów duplicated project on ballot {voter_id}: "
                    f"{ballot_project_ids}"
                )
            if self.enforce_one_per_category:
                categories = [
                    project_category.get(project_id)
                    for project_id in ballot_project_ids
                    if project_id in project_category
                ]
                if len(categories) != len(set(categories)):
                    raise RuntimeError(
                        f"Rzeszów ballot {voter_id} contains more than one "
                        f"project from a category: {ballot_project_ids}"
                    )

            for project_id in ballot_project_ids:
                district = project_pool.get(project_id)
                if district is None:
                    skipped_project_ids[project_id] = skipped_project_ids.get(project_id, 0) + 1
                    continue
                processed_rows.append(
                    {
                        "voter_id": voter_id,
                        "district": district,
                        "neighborhood": project_neighborhood[project_id],
                        "vote": str(project_id),
                        "voting_method": voting_method,
                    }
                )

        stats = {
            "valid_ballots": len(valid_votes),
            "valid_indications": len(processed_rows),
        }
        return pd.DataFrame(processed_rows), skipped_project_ids, stats

    def validate_vote_totals(self, projects_df, votes_df):
        counted_votes = votes_df.groupby("vote").size().to_dict()
        mismatches = []
        for _, project in projects_df.iterrows():
            counted = counted_votes.get(str(project["project_id"]), 0)
            if int(project["votes"]) != int(counted):
                mismatches.append(
                    {
                        "project_id": project["project_id"],
                        "official_votes": int(project["votes"]),
                        "counted_votes": int(counted),
                    }
                )
        if mismatches:
            raise RuntimeError(f"Rzeszów project vote mismatch: {mismatches[:20]}")

        official_project_ids = set(projects_df["project_id"].astype(str))
        ballot_project_ids = set(counted_votes)
        extra_project_ids = ballot_project_ids - official_project_ids
        if extra_project_ids:
            raise RuntimeError(
                "Rzeszów ballot project IDs absent from official results: "
                f"{sorted(extra_project_ids)}"
            )
        return counted_votes

    def validate_expected_totals(self, stats):
        expected = {
            "valid_ballots": self.expected_valid_ballots,
            "valid_indications": self.expected_valid_indications,
        }
        mismatches = {
            key: {"expected": value, "actual": stats[key]}
            for key, value in expected.items()
            if value is not None and value != stats[key]
        }
        if mismatches:
            raise RuntimeError(
                f"Unexpected Rzeszów source totals: {mismatches}"
            )

    def set_output_vote_totals(self, projects_df, counted_votes):
        if self.project_totals_output_source == "official_projects_results":
            return
        if (
            self.project_totals_output_source
            != "valid_ballots_after_matching_official_results"
        ):
            raise RuntimeError(
                "Unknown Rzeszów project totals output source: "
                f"{self.project_totals_output_source}"
            )
        projects_df["votes"] = projects_df["project_id"].map(counted_votes).fillna(0)
        projects_df["votes"] = projects_df["votes"].astype(int)

    def validate_selected(self, projects_df):
        selected_ids = set(projects_df[projects_df["selected"] == 1]["project_id"].astype(int))
        if selected_ids != self.accepted_project_ids:
            raise RuntimeError(
                "Rzeszów selected projects mismatch: "
                f"missing={sorted(self.accepted_project_ids - selected_ids)}, "
                f"extra={sorted(selected_ids - self.accepted_project_ids)}"
            )

    def start(self):
        self.logger.info("Running Rzeszów preprocessing...")
        (
            projects_df,
            project_pool,
            project_neighborhood,
            project_category,
        ) = self.load_projects()
        votes_df, skipped_project_ids, stats = self.load_votes(
            project_pool, project_neighborhood, project_category
        )

        counted_votes = self.validate_vote_totals(projects_df, votes_df)
        self.validate_expected_totals(stats)
        self.set_output_vote_totals(projects_df, counted_votes)
        self.validate_selected(projects_df)

        if skipped_project_ids:
            raise RuntimeError(
                f"Unexpected Rzeszów skipped project ids: {skipped_project_ids}"
            )

        projects_df.to_excel(self.get_output_path(self.projects_excel), index=False)
        votes_df.to_excel(self.get_output_path(self.votes_excel), index=False)
        self.logger.info("Rzeszów preprocessing finished!")
