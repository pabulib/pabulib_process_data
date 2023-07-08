from dataclasses import dataclass

import helpers.utilities as utils


@dataclass
class BaseConfig:
    country: str
    unit: str
    instance: int

    def __post_init__(self):
        self.logger = utils.create_logger()
        self.unit_file_name = f"{self.country}_{self.unit}_{self.instance}_"

    def save_mappings_as_jsons(self, objects):
        self.logger.info(f'Saving JSON files...')
        for obj_name, obj in objects.items():
            json_file_name = utils.create_json_file_name(
                self.country, self.unit, self.instance, obj_name)
            utils.save_dict_as_json(obj, json_file_name)
            self.logger.info(f'{json_file_name} file saved.')

    def get_json_file(self, file_name):
        return utils.name_and_load_dict_as_json(
            self.country, self.unit, self.instance, file_name)
