import os


pabulib_dir = os.path.join(os.getcwd(), "src")
path_to_excel_files = os.path.join(pabulib_dir, "data")
output_path = os.path.join(pabulib_dir, "output")

logging_level = 'DEBUG'


def get_path_to_excel_files(city_dir_name, extra_dir=""):
    path_to_excel_files = os.path.join(
        pabulib_dir, "data", city_dir_name, extra_dir)
    return path_to_excel_files


meta_fields_order = [
    "description",
    "country",
    "unit",
    "subunit",
    "instance",
    "num_projects",
    "num_votes",
    "budget",
    "leftover_budget",
    "budget_per_category",
    "budget_per_neighbourhood",
    "vote_type",
    "rule",
    "date_begin",
    "date_end",
    "language",
    "edition",
    "district",
    "comment",
    "min_length",
    "max_length",
    "min_sum_cost",
    "max_sum_cost",
    "scoring_fn",
    "min_points",
    "max_points",
    "min_sum_points",
    "max_sum_points",
    "default_score",
    "min_project_cost",
    "max_project_cost",
    "min_length_per_category",
    "max_length_per_category",
    "min_sum_cost_per_category",
    "max_sum_cost_per_category",
    "neighbourhoods",
    "subdistricts",
    "categories",
    "fully_funded",
    "currency",
    "acknowledgments"
]

projects_fields_order = [
    "project_id",
    "cost",
    "name",
    "category",
    "target",
    "votes",
    "score",
    "selected",
    "neighbourhood",
    "subunit",
    "district",
    "description",
    "proposer",
    "public_id",
    "longitude",
    "latitude"
]


votes_fields_order = [
    "voter_id",
    "age",
    "sex",
    "voting_method",
    "vote",
    "points",
    "district",
    "neighborhood",
    "education"
]
