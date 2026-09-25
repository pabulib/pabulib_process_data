districts = [
    "Bartodzieje",
    "Bielawy",
    "Bocianowo - Śródmieście - Stare Miasto",
    "Brdyujście",
    "Bydgoszcz Wschód - Siernieczek",
    "Błonie",
    "Czyżkówko",
    "Flisy",
    "Glinki - Rupienica",
    "Górzyskowo",
    "Jachcice",
    "Kapuściska",
    "Leśne",
    "Miedzyń - Prądy",
    "Nowy Fordon",
    "Okole",
    "Osowa Góra",
    "Piaski",
    "Smukała - Opławiec - Janowo",
    "Stary Fordon",
    "Szwederowo",
    "Tatrzańskie",
    "Tereny Nadwiślańskie",
    "Wilczak - Jary",
    "Wyżyny",
    "Wzgórze Wolności",
    "Zimne Wody - Czersko Polskie",
    "Łęgnowo",
    "Łęgnowo Wieś",
]

microproject_districts = [
    district for district in districts if district != "Wzgórze Wolności"
]

district_metadata = {
    **{
        district: {"subunit": district}
        for district in districts
    },
    **{
        f"{district} - mikroprojekty": {
            "description": (
                f"District PB in Bydgoszcz, {district} | small projects"
            ),
            "district": district,
            "subunit": f"{district} | small projects",
        }
        for district in microproject_districts
    },
    "Ponadosiedlowe": {
        "description": "Citywide project pool in Bydgoszcz",
        "subunit": "citywide projects",
        "remove_fields": ["district"],
    },
    "Społeczne": {
        "description": "Social project pool in Bydgoszcz",
        "subunit": "social projects",
        "remove_fields": ["district"],
        "comment": [
            "There is a difference between the number of votes in the file (198) and the official results (199) for project 371. Since the discrepancy concerns only one vote, we kept the number from the file (198) to maintain internal consistency."
        ],
    },
}

district_metadata["Błonie"]["comment"] = [
    "The budget was adjusted from 516,336 PLN to 516,338 PLN because the selected projects cost 516,338 PLN."
]

district_metadata["Bydgoszcz Wschód - Siernieczek"]["comment"] = [
    "The budget was adjusted from 347,171 PLN to 347,172 PLN because the selected projects cost 347,172 PLN."
]

district_metadata["Flisy"]["comment"] = [
    "The budget was adjusted from 182,687 PLN to 182,688 PLN because the selected projects cost 182,688 PLN."
]

district_metadata["Okole"]["comment"] = [
    "The budget was adjusted from 384,467 PLN to 384,468 PLN because the selected projects cost 384,468 PLN."
]

district_metadata["Szwederowo"]["comment"] = [
    "There is a difference between the number of votes in the file (173) and the official results (174) for project 466. Since the discrepancy concerns only one vote, we kept the number from the file (173) to maintain internal consistency."
]


all_data = {
    2025: {
        "base_data": {
            "country": "Poland",
            "unit": "Bydgoszcz",
            "instance": 2025,
        },
        "preprocess": {
            "data_dir": "2025",
            "source_votes_excel": "BBO_zestawienie_glosow_2025",
            "protocol_pdf": "Bydgoszcz_2025_protocol",
            "projects_excel": "Bydgoszcz_2025_projects_processed",
            "votes_excel": "Bydgoszcz_2025_votes_processed",
        },
        "get_projects": {
            "data_dir": "2025",
            "excel_filename": "Bydgoszcz_2025_projects_processed",
            "columns_mapping": {
                "project_id": "project_id",
                "name": "name",
                "cost": "cost",
                "votes": "votes",
                "district": "district",
                "selected": "selected",
            },
        },
        "get_votes": {
            "excel_filename": "Bydgoszcz_2025_votes_processed",
            "data_dir": "2025",
            "only_valid_votes": True,
            "voter_id_integer": False,
            "columns_mapping": {
                "voter_id": "voter_id",
                "sex": "sex",
                "age": "age",
                "vote_column": "vote",
                "district": "district",
                "voting_method": "voting_method",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_no_points",
        },
        "projects_data": {
            "unit_fields": ["project_id", "cost", "votes", "name", "selected"],
            "districts_fields": ["project_id", "cost", "votes", "name", "selected"],
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
            "districts_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
        },
        "metadata": {
            "vote_type": "choose-1",
            "rule": "greedy-no-skip",
            "min_project_score_threshold": "30",
            "date_begin": "03.11.2025",
            "date_end": "30.11.2025",
            "min_length": "1",
            "max_length": "1",
            "edition": "13",
            "language": "pl",
            "currency": "PLN",
            "description_prefix": "District PB",
            "district": {},
            "district_metadata": district_metadata,
        },
    },
}
