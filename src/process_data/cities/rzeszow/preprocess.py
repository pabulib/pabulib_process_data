import os
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

    def load_projects(self):
        raw_df = pd.read_excel(self.get_source_path(self.source_projects_excel), header=None)
        projects = []
        project_pool = {}
        project_neighborhood = {}
        current_category = None

        for _, row in raw_df.iterrows():
            first_cell = row.iloc[0]
            if isinstance(first_cell, str) and first_cell.startswith("KATEGORIA"):
                current_category = first_cell.strip()
                continue

            if not pd.notna(first_cell) or not isinstance(first_cell, (int, float)):
                continue

            project_id = int(first_cell)
            neighborhood = str(row.iloc[2]).strip()
            neighborhood_display = self.normalize_neighborhood(neighborhood)
            if current_category == "KATEGORIA II":
                pool = neighborhood
            else:
                pool = self.normalize_category(current_category)
            project_pool[project_id] = pool
            project_neighborhood[project_id] = neighborhood_display
            projects.append(
                {
                    "project_id": str(project_id),
                    "name": row.iloc[1],
                    "district": pool,
                    "neighborhood": neighborhood_display,
                    "category": self.normalize_category(current_category),
                    "source_district": row.iloc[2],
                    "cost": int(row.iloc[3]),
                    "votes": int(row.iloc[5]),
                    "selected": int(project_id in self.accepted_project_ids),
                }
            )

        for project in PROJECTS_MISSING_FROM_RESULTS:
            project_id = int(project["project_id"])
            if project_id not in project_pool:
                projects.append(project)
                project_pool[project_id] = project["district"]
                project_neighborhood[project_id] = self.normalize_neighborhood(
                    project["source_district"]
                )

        if len(projects) != 161:
            raise RuntimeError(f"Expected 161 Rzeszów projects, got {len(projects)}")

        return pd.DataFrame(projects), project_pool, project_neighborhood

    def normalize_voting_method(self, value):
        value = str(value).strip().lower()
        if value.startswith("elektronicz"):
            return "internet"
        if value.startswith("papier"):
            return "papier"
        raise RuntimeError(f"Unknown Rzeszów voting method: {value}")

    def load_votes(self, project_pool, project_neighborhood):
        votes_df = pd.read_excel(self.get_source_path(self.source_votes_excel), header=1)
        valid_votes = votes_df[votes_df["Ważność karty"] == "WAŻNA"]
        processed_rows = []
        skipped_project_ids = {}

        for _, row in valid_votes.iterrows():
            voter_id = int(row["Nr karty"])
            voting_method = self.normalize_voting_method(row["Wersja"])
            for raw_project_id in str(row["Oddane głosy"]).split(";"):
                raw_project_id = raw_project_id.strip()
                if not raw_project_id:
                    continue
                project_id = int(raw_project_id)
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

        return pd.DataFrame(processed_rows), skipped_project_ids

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
        projects_df, project_pool, project_neighborhood = self.load_projects()
        votes_df, skipped_project_ids = self.load_votes(
            project_pool, project_neighborhood
        )

        self.validate_vote_totals(projects_df, votes_df)
        self.validate_selected(projects_df)

        if skipped_project_ids:
            raise RuntimeError(
                f"Unexpected Rzeszów skipped project ids: {skipped_project_ids}"
            )

        projects_df.to_excel(self.get_output_path(self.projects_excel), index=False)
        votes_df.to_excel(self.get_output_path(self.votes_excel), index=False)
        self.logger.info("Rzeszów preprocessing finished!")
