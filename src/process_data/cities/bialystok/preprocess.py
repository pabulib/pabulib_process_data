import os
import re
import zipfile
from collections import Counter
from dataclasses import dataclass
from xml.etree import ElementTree as ET

import pandas as pd

import helpers.settings as helper_settings
from process_data.base_config import BaseConfig


PROJECT_TABLES = {
    0: ("M", "CITYWIDE"),
    2: ("O", "Osiedlowe"),
    4: ("Sz", "Szkolne"),
}

SELECTED_FILLS = {"FDE9D9", "FBE4D5"}


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    vote_pattern = re.compile(r"\bNr\s+((?:Sz|M|O)\d+)\.", re.IGNORECASE)
    valid_status = "ważny"

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_projects_docx = self.preprocess["source_projects_docx"]
        self.source_votes_excel = self.preprocess["source_votes_excel"]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        self.expected_projects = self.preprocess["expected_projects"]
        self.expected_selected_by_pool = self.preprocess[
            "expected_selected_by_pool"
        ]
        self.expected_valid_ballots = self.preprocess["expected_valid_ballots"]
        self.expected_valid_indications = self.preprocess[
            "expected_valid_indications"
        ]
        self.project_totals_output_source = self.preprocess[
            "project_totals_output_source"
        ]
        return super().__post_init__()

    def source_path(self, filename, extension):
        return os.path.join(
            helper_settings.get_path_to_excel_files(self.unit, self.data_dir),
            f"{filename}.{extension}",
        ).replace("\\", "/")

    def output_path(self, filename):
        return self.source_path(filename, "xlsx")

    @staticmethod
    def parse_int(value):
        digits = re.sub(r"\D", "", str(value))
        if not digits:
            raise RuntimeError(f"Białystok: cannot parse integer from {value!r}")
        return int(digits)

    @staticmethod
    def clean_text(value):
        text = str(value or "").replace("\xa0", " ")
        text = text.replace(";", "").replace('"', "")
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def normalize_project_id(value):
        match = re.fullmatch(r"(?i)(Sz|M|O)(\d+)", str(value).strip())
        if not match:
            raise RuntimeError(f"Białystok: invalid project ID {value!r}")
        prefix, number = match.groups()
        prefix = "Sz" if prefix.lower() == "sz" else prefix.upper()
        return f"{prefix}{number}"

    def iter_docx_tables(self):
        path = self.source_path(self.source_projects_docx, "docx")
        with zipfile.ZipFile(path) as docx:
            document_xml = docx.read("word/document.xml")

        namespace = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }
        root = ET.fromstring(document_xml)
        for table in root.findall(".//w:tbl", namespace):
            rows = []
            for table_row in table.findall("w:tr", namespace):
                cells = []
                for cell in table_row.findall("w:tc", namespace):
                    text = "".join(
                        text_node.text or ""
                        for text_node in cell.findall(".//w:t", namespace)
                    )
                    shading = cell.find("w:tcPr/w:shd", namespace)
                    fill = None
                    if shading is not None:
                        fill = shading.get(f"{{{namespace['w']}}}fill")
                    cells.append(
                        {
                            "text": text.replace("\xa0", " ").strip(),
                            "fill": fill,
                        }
                    )
                rows.append(cells)
            yield rows

    def parse_projects(self):
        projects = []
        for table_index, rows in enumerate(self.iter_docx_tables()):
            table_config = PROJECT_TABLES.get(table_index)
            if table_config is None:
                continue
            expected_prefix, district = table_config

            for row in rows:
                if not row or not row[0]["text"].rstrip(".").isdigit():
                    continue
                if district == "CITYWIDE":
                    if len(row) < 5:
                        raise RuntimeError("Białystok: incomplete citywide project row")
                    neighborhood = ""
                    cost_cell = row[3]["text"]
                    votes_cell = row[4]["text"]
                else:
                    if len(row) < 6:
                        raise RuntimeError("Białystok: incomplete local project row")
                    neighborhood = (
                        self.clean_text(row[3]["text"])
                        if district == "Osiedlowe"
                        else ""
                    )
                    cost_cell = row[4]["text"]
                    votes_cell = row[5]["text"]

                project_id = self.normalize_project_id(row[1]["text"])
                if not project_id.startswith(expected_prefix):
                    raise RuntimeError(
                        f"Białystok: project {project_id} in the wrong result table"
                    )
                projects.append(
                    {
                        "project_id": project_id,
                        "name": self.clean_text(row[2]["text"]),
                        "cost": self.parse_int(cost_cell),
                        "votes": self.parse_int(votes_cell),
                        "district": district,
                        "neighborhood": neighborhood,
                        "selected": int(row[0]["fill"] in SELECTED_FILLS),
                    }
                )

        projects_df = pd.DataFrame(projects)
        project_ids = projects_df["project_id"].tolist()
        if (
            len(projects_df) != self.expected_projects
            or len(set(project_ids)) != self.expected_projects
        ):
            raise RuntimeError(
                "Białystok: expected "
                f"{self.expected_projects} unique projects, got "
                f"{len(projects_df)} rows and {len(set(project_ids))} IDs"
            )

        selected_by_pool = (
            projects_df[projects_df["selected"] == 1]
            .groupby("district")
            .size()
            .to_dict()
        )
        if selected_by_pool != self.expected_selected_by_pool:
            raise RuntimeError(
                "Białystok: unexpected selected projects by pool: "
                f"{selected_by_pool}"
            )
        return projects_df

    @staticmethod
    def normalize_age(value):
        if pd.isna(value):
            return None
        return int(value)

    def parse_votes(self, projects_df):
        source = pd.read_excel(
            self.source_path(self.source_votes_excel, "xlsx"), sheet_name="Głosy"
        )
        required_columns = {
            "Lp.",
            "Typ głosu",
            "Status",
            "Nr projektów",
            "Płeć",
            "Wiek",
        }
        missing_columns = required_columns.difference(source.columns)
        if missing_columns:
            raise RuntimeError(
                f"Białystok: missing vote columns: {sorted(missing_columns)}"
            )

        valid = source[
            source["Status"].astype(str).str.strip().str.lower()
            == self.valid_status
        ]
        if valid["Lp."].duplicated().any():
            duplicates = valid.loc[valid["Lp."].duplicated(), "Lp."].tolist()
            raise RuntimeError(
                f"Białystok: duplicated valid ballot IDs: {duplicates[:20]}"
            )

        project_district = projects_df.set_index("project_id")["district"].to_dict()
        rows = []
        for _, ballot in valid.iterrows():
            project_ids = [
                self.normalize_project_id(project_id)
                for project_id in self.vote_pattern.findall(
                    str(ballot["Nr projektów"])
                )
            ]
            if not 1 <= len(project_ids) <= 4:
                raise RuntimeError(
                    f"Białystok: ballot {ballot['Lp.']} contains "
                    f"{len(project_ids)} project indications"
                )
            if len(project_ids) != len(set(project_ids)):
                raise RuntimeError(
                    f"Białystok: duplicate project on ballot {ballot['Lp.']}"
                )

            for project_id in project_ids:
                district = project_district.get(project_id)
                if district is None:
                    raise RuntimeError(
                        f"Białystok: project {project_id} from ballot "
                        f"{ballot['Lp.']} is absent from official results"
                    )
                rows.append(
                    {
                        "voter_id": int(ballot["Lp."]),
                        "vote": project_id,
                        "district": district,
                        "age": self.normalize_age(ballot["Wiek"]),
                        "sex": ballot["Płeć"],
                        "voting_method": ballot["Typ głosu"],
                    }
                )

        votes_df = pd.DataFrame(rows)
        if (
            len(valid) != self.expected_valid_ballots
            or len(votes_df) != self.expected_valid_indications
        ):
            raise RuntimeError(
                "Białystok: unexpected source totals: "
                f"valid ballots={len(valid)}, indications={len(votes_df)}"
            )
        return votes_df

    @staticmethod
    def validate_vote_totals(projects_df, votes_df):
        counted = Counter(votes_df["vote"].astype(str))
        mismatches = []
        for project in projects_df.itertuples():
            ballot_total = counted.get(str(project.project_id), 0)
            if ballot_total != int(project.votes):
                mismatches.append(
                    (str(project.project_id), int(project.votes), ballot_total)
                )
        if mismatches:
            raise RuntimeError(
                "Białystok: official results differ from ballot counts "
                f"(project_id, official, ballots): {mismatches[:20]}"
            )
        return counted

    def set_output_vote_totals(self, projects_df, counted_votes):
        if (
            self.project_totals_output_source
            != "valid_ballots_after_matching_official_results"
        ):
            raise RuntimeError(
                "Unknown Białystok project totals output source: "
                f"{self.project_totals_output_source}"
            )
        projects_df["votes"] = projects_df["project_id"].map(counted_votes).fillna(0)
        projects_df["votes"] = projects_df["votes"].astype(int)

    def save(self, dataframe, filename):
        dataframe.to_excel(self.output_path(filename), index=False)

    def start(self):
        self.logger.info("Running Białystok preprocessing...")
        projects_df = self.parse_projects()
        votes_df = self.parse_votes(projects_df)
        counted_votes = self.validate_vote_totals(projects_df, votes_df)
        self.set_output_vote_totals(projects_df, counted_votes)
        self.save(projects_df, self.projects_excel)
        self.save(votes_df, self.votes_excel)
        self.logger.info("Białystok preprocessing finished!")
