from dataclasses import dataclass
import os

import pandas as pd

import helpers.settings as helper_settings
from process_data.base_config import BaseConfig


DISTRICT_NAMES = {
    "Czechów Pd.": "Czechów Południowy",
    "Czechów Pł.": "Czechów Północny",
    "Czuby Pd.": "Czuby Południowe",
    "Czuby Płn.": "Czuby Północne",
    "Hajdów - Zadębie": "Hajdów-Zadębie",
    "Węglin Pd.": "Węglin Południowy",
    "Węglin Płn.": "Węglin Północny",
}


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.results_source = self.preprocess["results_source"]
        self.votes_source = self.preprocess["votes_source"]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        return super().__post_init__()

    def source_path(self, filename):
        return os.path.join(
            helper_settings.get_path_to_excel_files(self.unit, extra_dir=self.data_dir),
            filename,
        ).replace("\\", "/")

    def output_path(self, filename):
        return self.source_path(f"{filename}.xlsx")

    @staticmethod
    def normalize_district(value):
        if pd.isna(value):
            return ""
        value = str(value).strip()
        return DISTRICT_NAMES.get(value, value)

    def parse_projects(self):
        raw = pd.read_excel(
            self.source_path(self.results_source), sheet_name="Wszystkie ", header=None
        )
        winners_raw = pd.read_excel(
            self.source_path(self.results_source), sheet_name="zwycięskie", header=None
        )
        winners = winners_raw.iloc[1:].copy()
        winners = winners[winners.iloc[:, 2].notna()]
        selected_costs = {
            str(row.iloc[2]).strip(): int(row.iloc[3])
            for _, row in winners.iterrows()
        }

        section = None
        projects = []
        for _, row in raw.iterrows():
            first = row.iloc[0]
            if isinstance(first, str):
                marker = first.strip()
                if marker in ("DZIELNICOWE", "OGÓLNOMIEJSKIE"):
                    section = marker
                continue
            if pd.isna(first) or section is None:
                continue

            project_id = str(row.iloc[2]).strip()
            district = self.normalize_district(row.iloc[4])
            votes = row.iloc[5]
            if section == "DZIELNICOWE":
                pool = district
            elif pd.isna(votes):
                # Soft citywide rows have no district column, so their vote total
                # is shifted one cell left in the city's results workbook.
                votes = row.iloc[4]
                district = ""
                pool = "CITYWIDE_SOFT"
            else:
                pool = "CITYWIDE_HARD"

            cost = int(row.iloc[3])
            if project_id in selected_costs:
                # This also records the reduced final scope of O-67.
                cost = selected_costs[project_id]

            projects.append(
                {
                    "project_id": project_id,
                    "name": str(row.iloc[1]).strip(),
                    "cost": cost,
                    "votes": int(votes),
                    "district": pool,
                    "neighborhood": district,
                    "selected": int(project_id in selected_costs),
                }
            )

        projects_df = pd.DataFrame(projects)
        if len(projects_df) != 130:
            raise RuntimeError(f"Expected 130 Lublin projects, got {len(projects_df)}")
        if projects_df["project_id"].duplicated().any():
            raise RuntimeError("Duplicated project IDs in Lublin results")
        if len(selected_costs) != 39:
            raise RuntimeError(f"Expected 39 selected projects, got {len(selected_costs)}")

        selected = projects_df[projects_df["selected"] == 1]
        expected_selected_costs = {
            "district": 9_746_582,
            "hard": 6_075_098,
            "soft": 1_398_320,
            "total": 17_220_000,
        }
        actual_selected_costs = {
            "district": int(
                selected[~selected["district"].str.startswith("CITYWIDE")]["cost"].sum()
            ),
            "hard": int(
                selected[selected["district"] == "CITYWIDE_HARD"]["cost"].sum()
            ),
            "soft": int(
                selected[selected["district"] == "CITYWIDE_SOFT"]["cost"].sum()
            ),
            "total": int(selected["cost"].sum()),
        }
        if actual_selected_costs != expected_selected_costs:
            raise RuntimeError(
                "Unexpected selected-project costs: "
                f"{actual_selected_costs} != {expected_selected_costs}"
            )
        return projects_df

    def process_votes(self, projects_df):
        votes = pd.read_excel(self.source_path(self.votes_source))
        expected_columns = {
            "id",
            "uzytkownik_id",
            "rodzaj_glosowania",
            "plec",
            "data",
            "godzina",
            "numer_projektu",
        }
        if set(votes.columns) != expected_columns:
            raise RuntimeError(f"Unexpected Lublin vote columns: {list(votes.columns)}")
        if votes.isna().any().any():
            raise RuntimeError("Lublin votes contain missing values")
        if votes.duplicated().any():
            raise RuntimeError("Lublin votes contain duplicated rows")
        if votes.duplicated(["uzytkownik_id", "numer_projektu"]).any():
            raise RuntimeError("A Lublin voter selected the same project more than once")

        vote_counts = votes["numer_projektu"].astype(str).str.strip().value_counts()
        mismatches = []
        for _, project in projects_df.iterrows():
            counted = int(vote_counts.get(project["project_id"], 0))
            if counted != int(project["votes"]):
                mismatches.append(
                    (project["project_id"], int(project["votes"]), counted)
                )
        if mismatches:
            raise RuntimeError(f"Lublin official/ballot vote mismatch: {mismatches}")
        if set(vote_counts.index) - set(projects_df["project_id"]):
            raise RuntimeError("Lublin ballots contain unknown projects")

        per_voter = votes.groupby("uzytkownik_id")["numer_projektu"].agg(list)
        max_district = max(sum(str(v).startswith("D-") for v in row) for row in per_voter)
        max_citywide = max(sum(str(v).startswith("O-") for v in row) for row in per_voter)
        if (max_district, max_citywide) != (2, 2):
            raise RuntimeError(
                f"Unexpected ballot limits: district={max_district}, citywide={max_citywide}"
            )

        project_pools = projects_df.set_index("project_id")["district"].to_dict()
        processed = pd.DataFrame(
            {
                "voter_id": votes["uzytkownik_id"].astype(str),
                # Codes follow the same ordering as the earlier Lublin export:
                # 1 = man / internet, with the new value 2 used for woman.
                "sex": votes["plec"].map({1: "mężczyzna", 2: "kobieta"}),
                "voting_method": votes["rodzaj_glosowania"].map(
                    {1: "internetowe", 2: "papierowe"}
                ),
                "district": votes["numer_projektu"].map(project_pools),
                "vote": votes["numer_projektu"].astype(str).str.strip(),
            }
        )
        if processed.isna().any().any():
            raise RuntimeError("Could not normalize all Lublin vote rows")
        return processed

    def start(self):
        self.logger.info("Running Lublin 2026 preprocessing...")
        projects = self.parse_projects()
        votes = self.process_votes(projects)
        projects.to_excel(self.output_path(self.projects_excel), index=False)
        votes.to_excel(self.output_path(self.votes_excel), index=False)
