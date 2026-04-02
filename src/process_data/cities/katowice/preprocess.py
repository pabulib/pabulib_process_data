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
        self.data_dir = self.preprocess["data_dir"]
        return super().__post_init__()

    def get_projects_path(self):
        return utils.get_path_to_file_by_unit(
            self.excel_to_preprocess, self.unit, self.data_dir, ext="xlsx"
        )

    def get_votes_path(self):
        return utils.get_path_to_file_by_unit(
            self.votes_excel, self.unit, self.data_dir, ext="xlsx"
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

    def start(self):
        self.logger.info("Running preprocessing...")
        self.validate_votes_mapping()
        df = self.clean_projects(self.load_projects())
        df = self.add_votes_counts(df)
        output_path = utils.get_path_to_file_by_unit(
            self.output_excel_path, self.unit, self.data_dir, ext="xlsx"
        )
        df.to_excel(output_path, index=False)
        self.save_objects()
