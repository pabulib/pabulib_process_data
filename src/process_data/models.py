from dataclasses import dataclass
from typing import Union

import helpers.utilities as utils
import helpers.mappings as mapps


@dataclass
class ProjectItem:
    project_id: Union[int, str]
    cost: int = None
    category: str = None
    name: str = None
    target: str = None
    votes: int = None
    selected: int = None
    district: str = None
    district_upper: str = None
    project_url: str = None
    latitude: str = None
    longitude: str = None

    def add_district(self, district):
        self.district = district
        self.district_upper = utils.change_district_into_name(district)

    def add_category_from_list(self, category_list):
        self.category = ",".join(category_list)

    def add_cost(self, cost):
        self.cost = int(
            round(float(cost.replace("zł", "").replace(" ", "").replace(",", ".").strip())))

    def add_selected(self, status):
        self.selected = mapps.selected_mapping[status]

    def add_target(self, target_list):
        self.target = ",".join(target_list)

    def add_name(self, name):
        self.name = utils.clean_name(name)


@dataclass
class VoterItem:
    voter_id: Union[int, str]
    age: int = None
    sex: str = None
    voting_method: str = None
    vote: str = None
    # points: str = None
    neighborhood: str = None

    def add_vote(self, vote):
        self.vote = vote

    def add_age(self, age):
        if age:
            try:
                self.age = int(age)
            except ValueError:
                print(f'Cannot handle such age! {age}')

    def add_sex(self, sex):
        if sex:
            if sex.startswith('M'):
                self.sex = 'M'
            elif sex.startswith(('K', 'F')):
                self.sex = 'K'

    def add_voting_method(self, method):
        if method.lower() in ("elektronicznie", "internet"):
            self.voting_method = "internet"
        elif method.lower() in ("papierowo", "papier"):
            self.voting_method = "paper"

    def add_neighborhood(self, district):
        if district not in ('', None, '---'):
            self.neighborhood = district


@dataclass
class MetaItem:
    pass
