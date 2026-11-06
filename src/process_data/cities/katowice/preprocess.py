import re
from dataclasses import dataclass

import pandas as pd

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    district_code_mapping = {
        "M": "CITYWIDE",
        "L1": "Śródmieście",
        "L2": "Załęska Hałda - Brynów Część Zachodnia",
        "L3": "Zawodzie",
        "L4": "Osiedle Paderewskiego - Muchowiec",
        "L5": "Brynów Część Wschodnia - Osiedle Zgrzebnioka",
        "L6": "Ligota - Panewniki",
        "L7": "Załęże",
        "L8": "Osiedle Witosa",
        "L9": "Osiedle Tysiąclecia",
        "L10": "Dąb",
        "L11": "Wełnowiec - Józefowiec",
        "L12": "Koszutka",
        "L13": "Bogucice",
        "L14": "Dąbrówka Mała",
        "L15": "Szopienice - Burowiec",
        "L16": "Janów - Nikiszowiec",
        "L17": "Giszowiec",
        "L18": "Murcki",
        "L19": "Piotrowice - Ochojec",
        "L20": "Zarzecze",
        "L21": "Kostuchna",
        "L22": "Podlesie",
    }

    selected_mapping = {
        "wybrany": "wybrane",
        "wybrane": "wybrane",
        "wybrnany": "wybrane",
        "niewybrany": "niewybrane",
        "niewybrane": "niewybrane",
    }
    category_mapping = {
        "drogi/kominikacja": "drogi/komunikacja",
    }
    vote_district_code_mapping_2026 = {
        "Śródmieście": "L1",
        "Załęska Hałda- Brynów cz. zach.": "L2",
        "Zawodzie": "L3",
        "Os. Paderewskiego-Muchowiec": "L4",
        "Brynów cz. wsch.-Os. Zgrzebnioka": "L5",
        "Ligota-Panewniki": "L6",
        "Załęże": "L7",
        "Os. Witosa": "L8",
        "Os. Tysiąclecia": "L9",
        "Dąb": "L10",
        "Wełnowiec-Józefowiec": "L11",
        "Koszutka": "L12",
        "Bogucice": "L13",
        "Dąbrówka Mała": "L14",
        "Szopienice-Burowiec": "L15",
        "Janów-Nikiszowiec": "L16",
        "Giszowiec": "L17",
        "Murcki": "L18",
        "Piotrowice-Ochojec": "L19",
        "Zarzecze": "L20",
        "Kostuchna": "L21",
        "Podlesie": "L22",
    }
    selected_overrides = {
        # The source XLS and official city PDF disagree for Bogucice.
        # These overrides follow the official results PDF and the greedy-threshold rule.
        "L13/03/XII": "wybrane",
        "L13/10/XII": "niewybrane",
    }

    def __post_init__(self):
        self.excel_to_preprocess = self.preprocess["excel_to_preprocess"]
        self.output_excel_path = self.preprocess["output_excel_path"]
        self.votes_excel = self.preprocess["votes_excel"]
        self.votes_output_excel = self.preprocess.get("votes_output_excel")
        self.data_dir = self.preprocess["data_dir"]
        self.source_schema = self.preprocess.get("source_schema", "katowice_2025")
        self.expected_projects = self.preprocess.get("expected_projects")
        self.expected_selected = self.preprocess.get("expected_selected")
        self.expected_voters = self.preprocess.get("expected_voters")
        self.expected_vote_rows = self.preprocess.get("expected_vote_rows")
        self.expected_score = self.preprocess.get("expected_score")
        return super().__post_init__()

    def get_projects_path(self):
        return utils.get_path_to_file_by_unit(
            self.excel_to_preprocess, self.unit, self.data_dir, ext="xlsx"
        )

    def get_votes_path(self):
        return utils.get_path_to_file_by_unit(
            self.votes_excel, self.unit, self.data_dir, ext="xlsx"
        )

    def get_votes_output_path(self):
        return utils.get_path_to_file_by_unit(
            self.votes_output_excel, self.unit, self.data_dir, ext="xlsx"
        )

    def load_projects(self):
        df = pd.read_excel(self.get_projects_path())
        df.columns = [col.replace("\n", " ").strip() for col in df.columns]
        return df

    def clean_projects(self, df):
        df = df[df["NR ID"].notna()].copy()
        df["NR ID"] = df["NR ID"].astype(str).str.strip()
        df["district_code"] = df["NR ID"].str.extract(r"^(M|L\d+)")
        df["DZIELNICA"] = df["district_code"].map(self.district_code_mapping)
        if df["DZIELNICA"].isna().any():
            missing_codes = sorted(df[df["DZIELNICA"].isna()]["district_code"].unique())
            raise RuntimeError(f"Unknown Katowice district codes: {missing_codes}")
        selected_col = "WYBRANE / NIEWYBRANE W GŁOSOWANIU"
        df[selected_col] = (
            df[selected_col]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .map(self.selected_mapping)
            .fillna("")
        )
        df.loc[df["NR ID"].isin(self.selected_overrides), selected_col] = df[
            "NR ID"
        ].map(self.selected_overrides)
        category_col = "KATEGORIA PROJEKTU"
        df[category_col] = (
            df[category_col]
            .fillna("inne")
            .astype(str)
            .str.strip()
            .str.lower()
            .replace(self.category_mapping)
        )
        df = df.drop(columns=["district_code"])
        return df

    def validate_votes_mapping(self):
        votes = pd.read_excel(self.get_votes_path(), usecols=["DZIELNICA_KOD", "ID"])
        votes["district_code"] = votes["ID"].astype(str).str.extract(r"^(M|L\d+)")
        mismatches = votes[votes["DZIELNICA_KOD"] != votes["district_code"]]
        if not mismatches.empty:
            raise RuntimeError("Project IDs and district codes do not match in votes file.")

    def add_votes_counts(self, df):
        votes = pd.read_excel(self.get_votes_path(), usecols=["IDWPIS", "ID", "PUNKTY"])
        agg = (
            votes.groupby("ID")
            .agg(
                LICZBA_GLOSUJACYCH=("IDWPIS", "nunique"),
                SUMA_PUNKTOW=("PUNKTY", "sum"),
            )
            .reset_index()
        )
        df = df.merge(agg, left_on="NR ID", right_on="ID", how="left")
        df = df.drop(columns=["ID"])
        missing = df[df["LICZBA_GLOSUJACYCH"].isna()]["NR ID"].tolist()
        if missing:
            raise RuntimeError(f"Missing vote aggregates for projects: {missing}")
        df["LICZBA_GLOSUJACYCH"] = df["LICZBA_GLOSUJACYCH"].astype(int)
        df["SUMA_PUNKTOW"] = df["SUMA_PUNKTOW"].astype(int)
        return df

    def save_objects(self):
        objects = {
            "district_district_name_mapping": self.district_code_mapping,
        }
        self.save_mappings_as_jsons(objects)

    @staticmethod
    def normalize_title(value):
        text = str(value).replace("\xa0", " ")
        text = text.translate(str.maketrans({"„": '"', "”": '"', "“": '"'}))
        return re.sub(r"\s+", " ", text).strip().casefold()

    @staticmethod
    def normalize_project_name(value):
        text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
        text = re.sub(r'„([^\"]*)"', r"„\1”", text)
        return re.sub(r'"([^\"]*)"', r"„\1”", text)

    def load_2026_projects(self):
        projects = pd.read_excel(self.get_projects_path(), header=1)
        projects.columns = [
            re.sub(r"\s+", " ", str(column)).strip()
            for column in projects.columns
        ]
        required_columns = {
            "LICZBA UZYSKANYCH GŁOSÓW",
            "ID",
            "TYTUŁ ZADANIA",
            "WARTOŚĆ ZADANIA",
            "WYBRANE / NIEWYBRANE",
        }
        missing_columns = required_columns.difference(projects.columns)
        if missing_columns:
            raise RuntimeError(
                f"Missing Katowice project columns: {sorted(missing_columns)}"
            )

        projects = projects[projects["ID"].notna()].copy()
        projects["ID"] = projects["ID"].astype(str).str.strip()
        projects["district_code"] = projects["ID"].str.extract(
            r"^(M|L\d+)/", expand=False
        )
        projects["title_key"] = projects["TYTUŁ ZADANIA"].map(
            self.normalize_title
        )
        projects["official_score"] = projects[
            "LICZBA UZYSKANYCH GŁOSÓW"
        ].astype(int)
        projects["cost"] = projects["WARTOŚĆ ZADANIA"].astype(int)
        projects["selected"] = (
            projects["WYBRANE / NIEWYBRANE"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
            .map(self.selected_mapping)
        )

        if projects["district_code"].isna().any():
            invalid_ids = projects.loc[
                projects["district_code"].isna(), "ID"
            ].tolist()
            raise RuntimeError(f"Invalid Katowice project IDs: {invalid_ids[:20]}")
        if projects["selected"].isna().any():
            invalid_selected = sorted(
                projects.loc[
                    projects["selected"].isna(), "WYBRANE / NIEWYBRANE"
                ]
                .astype(str)
                .unique()
            )
            raise RuntimeError(
                f"Unknown Katowice selected values: {invalid_selected}"
            )

        duplicate_keys = projects.duplicated(
            ["title_key", "district_code"], keep=False
        )
        if duplicate_keys.any():
            duplicates = projects.loc[
                duplicate_keys, ["ID", "TYTUŁ ZADANIA", "district_code"]
            ].to_dict("records")
            raise RuntimeError(
                "Katowice project titles are not unique within a district: "
                f"{duplicates[:20]}"
            )
        return projects

    def load_and_match_2026_votes(self, projects):
        votes = pd.read_excel(self.get_votes_path())
        required_columns = {
            "IDWPIS",
            "WIEK",
            "PLEC",
            "TYP",
            "DZIELNICA_KOD",
            "STATUS_GLOSU",
            "PUNKTY",
            "TYTUL",
        }
        missing_columns = required_columns.difference(votes.columns)
        if missing_columns:
            raise RuntimeError(
                f"Missing Katowice vote columns: {sorted(missing_columns)}"
            )
        if not votes["STATUS_GLOSU"].eq(1).all():
            statuses = votes["STATUS_GLOSU"].value_counts(dropna=False).to_dict()
            raise RuntimeError(f"Unexpected Katowice vote statuses: {statuses}")

        votes = votes.copy()
        local_mask = votes["TYP"].eq("DZIELNICOWE")
        citywide_mask = votes["TYP"].eq("OGOLNOMIEJSKIE")
        if not (local_mask | citywide_mask).all():
            invalid_types = sorted(
                votes.loc[~(local_mask | citywide_mask), "TYP"].unique()
            )
            raise RuntimeError(f"Unknown Katowice vote types: {invalid_types}")

        votes["district_code"] = "M"
        votes.loc[local_mask, "district_code"] = votes.loc[
            local_mask, "DZIELNICA_KOD"
        ].map(self.vote_district_code_mapping_2026)
        if votes["district_code"].isna().any():
            invalid_districts = sorted(
                votes.loc[votes["district_code"].isna(), "DZIELNICA_KOD"]
                .astype(str)
                .unique()
            )
            raise RuntimeError(
                f"Unknown Katowice vote districts: {invalid_districts}"
            )

        votes["title_key"] = votes["TYTUL"].map(self.normalize_title)
        project_keys = projects[
            ["title_key", "district_code", "ID"]
        ].rename(columns={"ID": "matched_project_id"})
        votes = votes.merge(
            project_keys,
            on=["title_key", "district_code"],
            how="left",
            validate="many_to_one",
            sort=False,
        )
        if votes["matched_project_id"].isna().any():
            unmatched = votes.loc[
                votes["matched_project_id"].isna(),
                ["TYTUL", "DZIELNICA_KOD", "TYP"],
            ].drop_duplicates()
            raise RuntimeError(
                "Katowice vote titles could not be matched to official projects: "
                f"{unmatched.head(20).to_dict('records')}"
            )
        if votes.duplicated(["IDWPIS", "matched_project_id"]).any():
            duplicates = votes.loc[
                votes.duplicated(["IDWPIS", "matched_project_id"], keep=False),
                ["IDWPIS", "matched_project_id"],
            ].drop_duplicates()
            raise RuntimeError(
                "Katowice contains duplicated voter-project rows: "
                f"{duplicates.head(20).to_dict('records')}"
            )

        votes["ID"] = votes["matched_project_id"]
        votes["DZIELNICA_KOD"] = votes["district_code"]
        return votes.drop(
            columns=["title_key", "district_code", "matched_project_id"]
        )

    def validate_and_prepare_2026_projects(self, projects, votes):
        aggregates = (
            votes.groupby("ID")
            .agg(
                LICZBA_GLOSUJACYCH=("IDWPIS", "nunique"),
                BALLOT_SCORE=("PUNKTY", "sum"),
            )
            .reset_index()
        )
        projects = projects.merge(
            aggregates, on="ID", how="left", validate="one_to_one"
        )
        projects[["LICZBA_GLOSUJACYCH", "BALLOT_SCORE"]] = projects[
            ["LICZBA_GLOSUJACYCH", "BALLOT_SCORE"]
        ].fillna(0).astype(int)

        mismatches = projects[
            projects["official_score"] != projects["BALLOT_SCORE"]
        ]
        if not mismatches.empty:
            mismatch_details = mismatches[
                ["ID", "official_score", "BALLOT_SCORE"]
            ].head(20).to_dict("records")
            raise RuntimeError(
                "Katowice official project scores differ from ballot points: "
                f"{mismatch_details}"
            )

        actual = {
            "projects": len(projects),
            "selected": int(projects["selected"].eq("wybrane").sum()),
            "voters": int(votes["IDWPIS"].nunique()),
            "vote_rows": len(votes),
            "score": int(votes["PUNKTY"].sum()),
        }
        expected = {
            "projects": self.expected_projects,
            "selected": self.expected_selected,
            "voters": self.expected_voters,
            "vote_rows": self.expected_vote_rows,
            "score": self.expected_score,
        }
        unexpected = {
            key: {"expected": expected_value, "actual": actual[key]}
            for key, expected_value in expected.items()
            if expected_value is not None and expected_value != actual[key]
        }
        if unexpected:
            raise RuntimeError(f"Unexpected Katowice source totals: {unexpected}")

        return pd.DataFrame(
            {
                "NR ID": projects["ID"],
                "TYTUŁ ZADANIA": projects["TYTUŁ ZADANIA"].map(
                    self.normalize_project_name
                ),
                "KOSZT ZADANIA": projects["cost"],
                "WYBRANE / NIEWYBRANE W GŁOSOWANIU": projects["selected"],
                "DZIELNICA": projects["district_code"].map(
                    self.district_code_mapping
                ),
                "LICZBA_GLOSUJACYCH": projects["LICZBA_GLOSUJACYCH"],
                "SUMA_PUNKTOW": projects["official_score"],
            }
        )

    def start_2026(self):
        projects = self.load_2026_projects()
        votes = self.load_and_match_2026_votes(projects)
        processed_projects = self.validate_and_prepare_2026_projects(
            projects, votes
        )
        processed_projects.to_excel(
            utils.get_path_to_file_by_unit(
                self.output_excel_path, self.unit, self.data_dir, ext="xlsx"
            ),
            index=False,
        )
        votes.to_excel(self.get_votes_output_path(), index=False)
        self.save_objects()

    def start(self):
        self.logger.info("Running preprocessing...")
        if self.source_schema == "katowice_2026":
            self.start_2026()
            return
        self.validate_votes_mapping()
        df = self.clean_projects(self.load_projects())
        df = self.add_votes_counts(df)
        output_path = utils.get_path_to_file_by_unit(
            self.output_excel_path, self.unit, self.data_dir, ext="xlsx"
        )
        df.to_excel(output_path, index=False)
        self.save_objects()
