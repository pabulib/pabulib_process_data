"""Votes are combined in one cell: need to separate it."""

import pandas as pd

import helpers.utilities as utils

file_name = "Zadania_BO2024"
unit = "Częstochowa"
data_dir = "2024"

xls_path = utils.get_path_to_file_by_unit(file_name, unit, data_dir, ext="xls")

xlsx_path = utils.get_path_to_file_by_unit(file_name, unit, data_dir, ext="xlsx")


print(f"Loading `{xls_path}` file...")
sheet = utils.open_excel_workbook(xls_path, name="Dzielnicowe")
col_names_indexes = utils.get_col_names_indexes(sheet)
current_column_names = sheet.row_values(0)

data = []

for row_idx in range(1, sheet.nrows):
    row = sheet.row(row_idx)

    current_excel_data = {
        col_name: sheet.cell(row_idx, col_idx).value
        for col_idx, col_name in enumerate(current_column_names)
    }

    data.append(current_excel_data)

df = pd.DataFrame(data)

df.to_excel(xlsx_path, index=False)

print(f"Data successfully saved to {xlsx_path}")
