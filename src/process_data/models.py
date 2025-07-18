from dataclasses import dataclass
from typing import Union

import helpers.mappings as mapps
import helpers.utilities as utils


@dataclass
class ProjectItem:
    project_id: Union[int, str] = None
    cost: int = None
    category: str = None
    name: str = None
    target: str = None
    votes: int = None
    score: int = None
    selected: int = None
    district: str = None
    district_upper: str = None
    project_url: str = None
    latitude: str = None
    longitude: str = None

    def add_project_id(self, project_id):
        try:
            self.project_id = int(project_id)
        except ValueError:
            self.project_id = utils.clean_project_id(project_id)

    def add_district(self, district):
        self.district = district
        self.district_upper = utils.change_district_into_name(district)

    def add_votes(self, votes):
        try:
            self.votes = int(votes)
        except ValueError:
            self.votes = int(votes.replace(" ", ""))

    def add_score(self, score):
        try:
            self.score = int(score)
        except ValueError:
            self.score = int(score.replace(" ", ""))

    def add_category_from_list(self, category_list):
        self.category = ",".join(category_list)

    def add_cost(self, cost):
        if cost == "":
            print(
                f"Project without cost!!! `{self.name}`, project ID: {self.project_id}"
            )
            # raise RuntimeError
            self.cost = "0"
        else:
            self.cost = int(
                round(
                    float(
                        str(cost)
                        .replace("zł", "")
                        .replace("PLN", "")
                        .replace(" ", "")
                        .replace(",", ".")
                        .replace("\xa0", "")
                        .strip()
                    )
                )
            )

    def add_selected(self, status):
        try:
            self.selected = int(status)
        except ValueError:
            self.selected = mapps.selected_mapping[status.lower()]

    def add_target(self, target_list):
        self.target = ",".join(target_list)

    def add_name(self, name):
        self.name = utils.clean_name(name)

    def add_subdistrict(self, subdistrict):
        if not subdistrict:
            raise RuntimeError("There is no subdistrict you are trying to add!")
        if subdistrict.lower() in ("mały"):
            self.subdistrict = "small"
        elif subdistrict.lower() in ("duży"):
            self.subdistrict = "large"
        else:
            self.subdistrict = subdistrict


@dataclass
class VoterItem:
    voter_id: Union[int, str]
    age: int = None
    sex: str = None
    voting_method: str = None
    vote: str = None
    points: str = None
    neighborhood: str = None

    def add_vote(self, vote):
        self.vote = vote

    def add_age(self, age):
        if age:
            try:
                self.age = int(age)
            except ValueError:
                print(f"Cannot handle such age! {age}")

    def add_sex(self, sex):
        if sex:
            if sex.lower().startswith("m"):
                self.sex = "M"
            elif sex.lower().startswith(("k", "f")):
                self.sex = "F"

    def add_voting_method(self, method):
        if method.lower() in (
            "elektronicznie",
            "internet",
            "internetowe",
            "i",
            "e",
            "elektroniczny",
        ):
            self.voting_method = "internet"
        elif method.lower() in ("papierowo", "papier", "papierowe", "p"):
            self.voting_method = "paper"

    def add_neighborhood(self, district):
        if district not in ("", None, "---"):
            self.neighborhood = district


@dataclass
class MetaItem:
    pass
