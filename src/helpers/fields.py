import re

COUNTRIES = [
    "Poland",
    "Netherlands",
    "Canada",
    "US",
    "France",
    "Worldwide",
    "Switzerland",
]
VOTE_TYPES = ["ordinal", "approval", "cumulative", "choose-1"]
RULES = [
    "greedy",
    "unknown",
    "equalshares",
    "equalshares/add1",
]


def validate_date_format(value):
    """
    Validate that a date string matches either 'YYYY' or 'DD.MM.YYYY' format.
    Returns True if valid, otherwise False.
    """
    if re.match(r"^\d{4}$", value) or re.match(r"^\d{2}\.\d{2}\.\d{4}$", value):
        return True
    return False


def validate_currency_code(value, *args):
    """
    Validate that the currency code is in ISO 4217 format (three-letter code).
    Returns True if valid, otherwise an error message.
    """
    import pycountry

    if pycountry.currencies.get(alpha_3=value) is None:
        return f"wrong currency ISO 4217 format code: {value}"
    return True


def validate_language_code(value, *args):
    """
    Validate that the language code is in ISO 639-1 format (two-letter code).
    Returns True if valid, otherwise an error message.
    """
    import pycountry

    if pycountry.languages.get(alpha_2=value) is None:
        return f"wrong language ISO 639-1 format code: {value}"
    return True


def validate_list(value, *args):
    """
    Validate that the value is a list.
    Returns True if valid, otherwise an error message.
    """
    if not isinstance(value, list):
        return f"Expected a list, but found {type(value).__name__}."
    return True


META_FIELDS_ORDER = {
    "description": {"datatype": str, "obligatory": True},
    "country": {
        "datatype": str,
        "checker": lambda x: x in COUNTRIES,
        "obligatory": True,
    },
    "unit": {"datatype": str, "obligatory": True},
    "district": {"datatype": str},
    "subunit": {"datatype": str},
    "instance": {"datatype": str, "obligatory": True},
    "num_projects": {"datatype": int, "obligatory": True},
    "num_votes": {"datatype": int, "obligatory": True},
    "budget": {"datatype": float, "obligatory": True},
    "leftover_budget": {"datatype": str},
    "budget_per_category": {"datatype": list, "checker": validate_list},
    "budget_per_neighbourhood": {"datatype": list, "checker": validate_list},
    "vote_type": {
        "datatype": str,
        "checker": lambda x: x in VOTE_TYPES,
        "obligatory": True,
    },
    "rule": {"datatype": str, "checker": lambda x: x in RULES, "obligatory": True},
    # change on page that dates are obligatory
    "date_begin": {
        "datatype": str,
        "checker": validate_date_format,
        "obligatory": True,
    },
    "date_end": {"datatype": str, "checker": validate_date_format, "obligatory": True},
    "min_length": {"datatype": int},
    "max_length": {"datatype": int},
    "min_sum_cost": {"datatype": float},
    "max_sum_cost": {"datatype": float},
    "scoring_fn": {"datatype": str},
    "min_points": {"datatype": int},
    "max_points": {"datatype": int},
    "min_sum_points": {"datatype": int},
    "max_sum_points": {"datatype": int},
    "default_score": {"datatype": float},
    "min_project_cost": {"datatype": int},
    "max_project_cost": {"datatype": int},
    "min_length_per_category": {"datatype": int},
    "max_length_per_category": {"datatype": int},
    "min_sum_cost_per_category": {"datatype": list, "checker": validate_list},
    "max_sum_cost_per_category": {"datatype": list, "checker": validate_list},
    "neighbourhoods": {"datatype": str},
    "subdistricts": {"datatype": str},
    "categories": {"datatype": str},
    "fully_funded": {"datatype": bool, "checker": lambda x: x in [1]},
    "experimental": {"datatype": bool, "checker": lambda x: x in [1]},
    "language": {
        "datatype": str,
        "checker": validate_language_code,
    },
    "edition": {"datatype": str},
    "currency": {
        "datatype": str,
        "checker": validate_currency_code,
    },
    "acknowledgments": {"datatype": str},
    "comment": {"datatype": str, "checker": lambda x: x.startswith("#1: ")},
}

PROJECTS_FIELDS_ORDER = {
    "project_id": {"datatype": list, "checker": validate_list, "obligatory": True},
    "votes": {"datatype": list, "checker": validate_list},
    "score": {"datatype": list, "checker": validate_list},
    "cost": {"datatype": int, "obligatory": True},
    "name": {"datatype": str},
    "category": {"datatype": list, "checker": validate_list, "nullable": True},
    "target": {"datatype": list, "checker": validate_list, "nullable": True},
    "selected": {"datatype": bool, "checker": lambda x: x in [1, 2, 3]},
    "neighbourhood": {"datatype": str},
    "neighborhood": {"datatype": str},
    "subunit": {"datatype": str},
    "district": {"datatype": str},
    "description": {"datatype": str},
    "proposer": {"datatype": str},
    "public_id": {"datatype": str},
    "longitude": {"datatype": float, "nullable": True},
    "latitude": {"datatype": float, "nullable": True},
}


VOTES_FIELDS_ORDER = {
    "voter_id": {"datatype": str, "obligatory": True},
    "vote": {"datatype": list, "checker": validate_list, "obligatory": True},
    "points": {"datatype": list, "checker": validate_list},
    "age": {"datatype": int, "nullable": True},
    "sex": {
        "datatype": str,
        "checker": lambda x: x in ["M", "F"],
    },  # Example values
    "voting_method": {"datatype": str},
    "district": {"datatype": str, "nullable": True},
    "neighborhood": {"datatype": str},
    "education": {"datatype": str},
    # Switzerland-specific fields
    "topic_preference_transport": {"datatype": int},
    "topic_preference_culture": {"datatype": int},
    "topic_preference_nature": {"datatype": int},
    "district_preference": {"datatype": str},
    "time_taken_seconds": {"datatype": int},
    "format_easiness": {"datatype": str},
    "format_expressiveness": {"datatype": str},
    "format_rank": {"datatype": str},
}
