import os
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from xml.etree import ElementTree as ET

import pandas as pd

import helpers.settings as helper_settings
from process_data.base_config import BaseConfig


CATEGORY_MAPPING = {
    "Do 100 tys. zł": "small",
    "od 100 do 600 tys. zł": "medium",
    "Powyżej 600 tys. zł": "large",
}


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_excel = self.preprocess["source_excel"]
        self.winners_docx = self.preprocess["winners_docx"]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        return super().__post_init__()

    def get_raw_path(self, filename, ext):
        return os.path.join(
            helper_settings.get_path_to_excel_files(self.unit, self.data_dir),
            "raw",
            f"{filename}.{ext}",
        ).replace("\\", "/")

    def get_output_path(self, filename):
        output_dir = helper_settings.get_path_to_excel_files(
            self.unit, extra_dir=self.data_dir
        )
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{filename}.xlsx").replace("\\", "/")

    def normalize_text(self, value):
        text = str(value or "").replace("\xa0", " ").strip().lower()
        text = unicodedata.normalize("NFKD", text)
        text = "".join(ch for ch in text if not unicodedata.combining(ch))
        return re.sub(r"[^a-z0-9]+", " ", text).strip()

    def parse_cost(self, value):
        return int(str(value).replace("zł", "").replace(" ", "").replace("\xa0", ""))

    def clean_text_field(self, value):
        text = str(value or "").replace("\xa0", " ")
        text = text.replace(";", "").replace('"', "")
        return re.sub(r"\s+", " ", text).strip()

    def read_source(self):
        path = self.get_raw_path(self.source_excel, "xlsx")
        return {
            "online": pd.read_excel(path, sheet_name="Głosy online"),
            "paper": pd.read_excel(path, sheet_name="Głosy papierowe"),
            "results": pd.read_excel(path, sheet_name="Wyniki"),
        }

    def iter_docx_tables(self):
        path = self.get_raw_path(self.winners_docx, "docx")
        with zipfile.ZipFile(path) as docx:
            xml = docx.read("word/document.xml")
        root = ET.fromstring(xml)
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        for table in root.findall(".//w:tbl", namespace):
            rows = []
            for table_row in table.findall("w:tr", namespace):
                cells = []
                for cell in table_row.findall("w:tc", namespace):
                    texts = [
                        text_node.text or ""
                        for text_node in cell.findall(".//w:t", namespace)
                    ]
                    cells.append("".join(texts).replace("\xa0", " ").strip())
                rows.append(cells)
            yield rows

    def load_winning_projects(self, results_df):
        title_to_project = {
            self.normalize_text(row["Tytuł projektu"]): int(row["Nr projektu"])
            for _, row in results_df.iterrows()
        }
        selected = {}

        for table_idx, rows in enumerate(self.iter_docx_tables()):
            for row_idx, row in enumerate(rows):
                if table_idx < 3:
                    if row_idx < 2 or len(row) < 5 or not row[0].isdigit():
                        continue
                    title = row[1]
                    selected_value = 1
                else:
                    if row_idx < 2 or len(row) < 4 or not row[0]:
                        continue
                    title = row[0]
                    selected_value = 2

                try:
                    project_id = title_to_project[self.normalize_text(title)]
                except KeyError as exc:
                    raise RuntimeError(f"Cannot match Radom winning project: {title}") from exc
                selected[project_id] = selected_value

        if len(selected) != 40:
            raise RuntimeError(f"Expected 40 Radom winners, got {len(selected)}")
        return selected

    def prepare_projects(self, results_df, selected):
        projects_df = pd.DataFrame(
            {
                "project_id": results_df["Nr projektu"].astype(int),
                "name": results_df["Tytuł projektu"].map(self.clean_text_field),
                "cost": results_df["Koszt"].astype(int),
                "score": results_df["Ostateczna liczba punktów"].astype(int),
                "district": results_df["Kategoria"].map(CATEGORY_MAPPING),
                "selected": results_df["Nr projektu"].map(selected).fillna(0).astype(int),
                "neighborhood": results_df["Lokalizacja"].map(self.clean_text_field),
            }
        )
        if projects_df["district"].isna().any():
            missing = sorted(results_df[projects_df["district"].isna()]["Kategoria"].unique())
            raise RuntimeError(f"Unknown Radom categories: {missing}")
        projects_df = projects_df.sort_values(["district", "score"], ascending=[True, False])
        projects_df.to_excel(self.get_output_path(self.projects_excel), index=False)
        return projects_df

    def choose_invalid_points_to_remove(self, counts, invalid_points):
        for threes in range(min(counts[3], invalid_points // 3), -1, -1):
            remainder_after_threes = invalid_points - 3 * threes
            for twos in range(min(counts[2], remainder_after_threes // 2), -1, -1):
                ones = remainder_after_threes - 2 * twos
                if ones <= counts[1]:
                    return {1: ones, 2: twos, 3: threes}
        raise RuntimeError(
            f"Cannot remove {invalid_points} invalid points from counts {dict(counts)}"
        )

    def build_raw_vote_rows(self, online_df, paper_df, project_categories):
        rows = []
        for _, row in online_df.iterrows():
            project_id = int(row["Projekt"])
            rows.append(
                {
                    "project_id": project_id,
                    "points": int(row["Punkty"]),
                    "district": project_categories[project_id],
                    "voting_method": "internet",
                }
            )

        for _, row in paper_df.iterrows():
            project_id = int(row["Projekt"])
            for points, column in ((1, "1 punkt"), (2, "2 punkty"), (3, "3 punkty")):
                for _ in range(int(row[column])):
                    rows.append(
                        {
                            "project_id": project_id,
                            "points": points,
                            "district": project_categories[project_id],
                            "voting_method": "papier",
                        }
                    )
        return rows

    def prepare_votes(self, source, projects_df):
        project_categories = projects_df.set_index("project_id")["district"].to_dict()
        rows = self.build_raw_vote_rows(
            source["online"], source["paper"], project_categories
        )
        invalid_by_project = source["results"].set_index("Nr projektu")[
            "Punkty nieważne"
        ].astype(int).to_dict()
        counts_by_project = defaultdict(Counter)
        for row in rows:
            counts_by_project[row["project_id"]][row["points"]] += 1

        to_remove = {
            project_id: self.choose_invalid_points_to_remove(
                counts_by_project[project_id], invalid_points
            )
            for project_id, invalid_points in invalid_by_project.items()
            if invalid_points
        }

        valid_rows = []
        for row in rows:
            project_remove = to_remove.get(row["project_id"], {})
            if project_remove.get(row["points"], 0):
                project_remove[row["points"]] -= 1
                continue
            valid_rows.append(row)

        votes_df = pd.DataFrame(valid_rows)
        votes_df.insert(0, "voter_id", range(1, len(votes_df) + 1))
        votes_df = votes_df.rename(columns={"project_id": "vote"})
        votes_df = votes_df[["voter_id", "vote", "points", "district", "voting_method"]]

        official_scores = projects_df.set_index("project_id")["score"].to_dict()
        counted_scores = votes_df.groupby("vote")["points"].sum().astype(int).to_dict()
        mismatches = []
        for project_id, official_score in official_scores.items():
            counted_score = counted_scores.get(project_id, 0)
            if counted_score != official_score:
                mismatches.append((project_id, official_score, counted_score))
        if mismatches:
            raise RuntimeError(f"Radom vote score mismatches: {mismatches[:20]}")

        votes_df.to_excel(self.get_output_path(self.votes_excel), index=False)

    def start(self):
        self.logger.info("Running Radom preprocessing...")
        source = self.read_source()
        selected = self.load_winning_projects(source["results"])
        projects_df = self.prepare_projects(source["results"], selected)
        self.prepare_votes(source, projects_df)
        self.logger.info("Radom preprocessing finished!")
