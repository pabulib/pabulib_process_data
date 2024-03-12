import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict = None

    def __post_init__(self):
        self.excel_filename = self.preprocess["excel_filename"]
        self.data_dir = self.preprocess["data_dir"]
        return super().__post_init__()

    def load_csv(self):
        self.logger.info("Preprocessing: load CSV...")
        csv_path = utils.get_path_to_file_by_unit(
            self.excel_filename, self.unit, self.data_dir, ext="csv"
        )
        df = pd.read_csv(csv_path, delimiter=";")
        return df

    def transform_df(self, df):
        self.logger.info("Preprocessing: transform df...")
        df = df.replace(0, np.nan)
        citywide_df = df.filter(regex="OGM*", axis=1)
        district_df = df.filter(regex="^(?!.*OGM).*\/\d{4}", axis=1)

        result = df.iloc[:, :4]

        result["citywide_vote"] = (
            citywide_df.stack()
            .reset_index()
            .groupby("level_0")["level_1"]
            .transform(lambda x: ",".join(x))
        )
        result["district_vote"] = (
            district_df.stack()
            .reset_index()
            .groupby("level_0")["level_1"]
            .transform(lambda x: ",".join(x))
        )

        # to remove voter_id == 0
        result.index = np.arange(1, len(df) + 1)
        return result

    def start(self):
        self.logger.info("Running preprocessing...")
        excel_path = utils.get_path_to_file_by_unit(
            self.excel_filename, self.unit, self.data_dir, ext="xlsx"
        )
        if os.path.exists(excel_path):
            self.logger.info(
                "There is already existing Excel file, preprocessing "
                "stopped. If you want to convert anyway, "
                f"please remove xlsx {excel_path}"
            )
        else:
            self.preprocess_csv(excel_path)

    def preprocess_csv(self, excel_path):
        df = self.load_csv()
        df = self.transform_df(df)
        print(df.head())
        self.logger.info("Preprocessing: save df to Excel...")
        df.to_excel(excel_path, index_label="voter_id")
