all_data = {
    2024: {
        "base_data": {
            "country": "Poland",
            "unit": "Częstochowa",
            "instance": 2024,
        },
        "preprocess": {
            "votes_xls": "Głosy_BO2024",
            "projects_xls": "Zadania_BO2024",
            "data_dir": "2024",
        },
        "get_projects": {
            "data_dir": "2024",
            "excel_filename": "Zadania_BO2024",
            "columns_mapping": {
                "project_id": "Nr zadania",
                "name": "Zadanie",
                "cost": "Koszt",
                "score": "Punkty WAŻNE",
                "votes": "Głosy WAŻNE:",
                "district": "district",
                "selected": "Selected",  # Added manually from cell colours
            },
        },
        "get_votes": {
            "excel_filename": "Głosy_BO2024",
            "data_dir": "2024",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "Lp.",
                "voting_method": "TYP",
                "sex": "Płeć",
                "points": "pkt",
                "vote_column": "nr",
                "district": "district",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_with_points",
        },
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "score",
                "name",
                "selected",
            ]
        },
        "votes_data": {
            "unit_fields": [
                "voter_id",
                "sex",
                "vote",
                "points",
                "voting_method",
                "neighborhood",
            ],
            "districts_fields": ["voter_id", "sex", "vote", "points", "voting_method"],
        },
        "metadata": {
            "vote_type": "cumulative",
            "rule": "greedy",
            "date_begin": "07.09.2023",
            "date_end": "21.09.2023",
            "language": "pl",
            "max_sum_points": "10",
            "edition": "10",
            "currency": "PLN",
            "unit": {},
            "district": {},
        },
    },
}
