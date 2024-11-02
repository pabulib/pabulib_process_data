"""Votes are combined in one cell: need to separate it."""

import re
from dataclasses import dataclass

import pandas as pd

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict = None

    def __post_init__(self):
        self.votes_excel = self.preprocess["votes_xls"]
        self.projects_excel = self.preprocess["projects_xls"]
        self.data_dir = self.preprocess["data_dir"]
        return super().__post_init__()

    def get_votes_data(self):
        excel_path = utils.get_path_to_file_by_unit(
            self.votes_excel, self.unit, self.data_dir, ext="xls"
        )
        self.logger.info(f"Loading `{excel_path}` file...")
        sheet = utils.open_excel_workbook(excel_path)
        col_names_indexes = utils.get_col_names_indexes(sheet)
        current_column_names = sheet.row_values(0)

        data = []

        pattern = r"(\d+)\s*PKT\s*-\s*Nr\s*(\d+)"

        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)

            cell_value = row[col_names_indexes["Nr zadań"]].value

            current_excel_data = {
                col_name: sheet.cell(row_idx, col_idx).value
                for col_idx, col_name in enumerate(current_column_names)
            }

            matches = re.findall(pattern, cell_value)

            for match in matches:
                pkt, nr = match
                district = self.project_id_district_mapping[int(nr)]
                data.append(
                    {"pkt": pkt, "nr": nr, "district": district, **current_excel_data}
                )

        return data

    def get_projects_data(self):
        excel_path = utils.get_path_to_file_by_unit(
            self.projects_excel, self.unit, self.data_dir, ext="xls"
        )
        self.logger.info(f"Loading `{excel_path}` file...")

        self.project_id_district_mapping = {}

        citywide_sheet = utils.open_excel_workbook(excel_path, name="Ogólnomiejskie")
        district_sheet = utils.open_excel_workbook(excel_path, name="Dzielnicowe")

        data = []

        for sheet_name, sheet in [
            ("Ogólnomiejskie", citywide_sheet),
            ("Dzielnicowe", district_sheet),
        ]:

            col_names_indexes = utils.get_col_names_indexes(sheet)

            if sheet_name == "Ogólnomiejskie":
                current_district = "Ogólnomiejskie"
            else:
                current_district = None  # To store the current district name

            for row_idx in range(1, sheet.nrows):
                row = sheet.row(row_idx)

                # Check if this row is likely a district name (e.g., "Błeszno" or "Częstochówka - Parkitka")
                # Typically, district names are in the first column, and we skip if it's "Miejsce" or contains "Głosów ważnych"
                if (
                    isinstance(row[0].value, str)
                    and row[0].value not in ["Miejsce"]
                    and "Głosów ważnych" not in row[0].value
                ):
                    # Update current district and skip this row as it only holds the district name
                    current_district = row[0].value
                    continue

                # Skip rows with "Głosów ważnych" and repeated headers (like "Miejsce")
                if isinstance(row[0].value, str) and (
                    "Głosów ważnych" in row[0].value or row[0].value == "Miejsce"
                ):
                    continue

                # Collect the current row's data using the column headers from the first row
                current_data = {
                    col_name: sheet.cell(row_idx, col_idx).value
                    for col_idx, col_name in enumerate(sheet.row_values(0))
                }

                # Add the district name and sheet name to the current row's data
                if current_district:
                    current_data["district"] = current_district
                current_data["sheet_name"] = (
                    sheet_name  # Add sheet name (e.g., "citywide" or "district")
                )

                # Append the row data with additional fields to the main data list
                data.append(current_data)

                project_id = int(row[col_names_indexes["Nr zadania"]].value)
                self.project_id_district_mapping[project_id] = current_district

        return data

    def save_new_xlsx(self, filename, data):
        df = pd.DataFrame(data)

        output_file_path = utils.get_path_to_file_by_unit(
            filename, self.unit, self.data_dir, ext="xlsx"
        )

        df.to_excel(output_file_path, index=False)

        self.logger.info(f"Data successfully saved to {output_file_path}")

    def start(self):
        self.logger.info("Running preprocessing...")

        projects_data = self.get_projects_data()
        self.save_new_xlsx(self.projects_excel, projects_data)

        votes_data = self.get_votes_data()
        self.save_new_xlsx(self.votes_excel, votes_data)

        self.logger.info("Preprocessing finished!")
