META_OBLIGATORY_FIELDS = [
    "description",
    "country",
    "unit",
    "instance",
    "num_projects",
    "num_votes",
    "budget",
    "vote_type",
    "rule",
    "date_begin",  # change on page that is obligatory
    "date_end",  # change on page that is obligatory
]

META_FIELDS_ORDER = [
    "description",
    "country",
    "unit",
    "district",
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
    "experimental",
    "language",
    "edition",
    "currency",
    "acknowledgments",
    "comment",
]

PROJECT_OBLIGATORY_FIELDS = [
    "project_id",
    "cost",
]

PROJECT_FIELDS_ORDER = [
    "project_id",
    "votes",
    "score",
    "cost",
    "name",
    "category",
    "target",
    "selected",
    "neighbourhood",
    "subunit",
    "district",
    "description",
    "proposer",
    "public_id",
    "longitude",
    "latitude",
]

VOTES_OBLIGATORY_FIELDS = [
    "voter_id",
    "vote",
]

VOTES_FIELDS_ORDER = [
    "voter_id",
    "vote",
    "points",
    "age",
    "sex",
    "voting_method",
    "district",
    "neighborhood",
    "education",
]
