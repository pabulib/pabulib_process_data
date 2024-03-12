from dataclasses import dataclass

import helpers.utilities as utils
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.excel_to_preprcess = self.preprocess["excel_to_preprocess"]
        self.data_dir = self.preprocess["data_dir"]
        return super().__post_init__()

    def start(self):
        self.logger.info("Running preprocessing...")
        excel_path = utils.get_path_to_file_by_unit(
            self.excel_to_preprcess, self.unit, self.data_dir, ext="xlsx"
        )
        print(excel_path)
        raise RuntimeError
