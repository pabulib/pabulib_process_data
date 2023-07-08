import collections
from dataclasses import dataclass

import helpers.utilities as utils
from process_data.base_config import BaseConfig
from process_data.models import ProjectItem


@dataclass
class GetProjects(BaseConfig):
    district_projects: bool = True

    def __post_init__(self):
        self.logger = utils.create_logger()
        self.initialize_mapping_dicts()
        return super().__post_init__()

    def initialize_mapping_dicts(self):
        self.projects_data_per_district = collections.defaultdict(list)
        self.district_projects_mapping = collections.defaultdict(list)
        self.project_district_mapping = dict()

    def iterate_through_projects(self):
        pass

    def create_project_item(self):
        project_id = None
        item = ProjectItem(project_id)
        name = None
        item.add_name(name)
        district = None
        self.logger.info(f'Processing Project: {project_id}')
        item.add_district(district.strip())
        item.project_url = None
        cost = None
        item.add_cost(cost)
        status = None
        item.add_selected(status)
        item.votes = None

        return item

    def start(self):
        self.iterate_through_projects()
        objects = {
            'district_projects_mapping': self.district_projects_mapping,
            'projects_data_per_district': self.projects_data_per_district,
            'project_district_mapping': self.project_district_mapping,
        }
        self.save_mappings_as_jsons(objects)
