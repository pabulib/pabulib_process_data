all_data = {
    2027: {
        "base_data": {
            "country": "Poland",
            "unit": "Olsztyn",
            "instance": 2027,
        },
        "preprocess": {
            "data_dir": "2027",
            "source_votes_excel": "Olsztyn_2027_votes_source",
            "projects_excel": "Olsztyn_2027_projects_processed",
            "votes_excel": "Olsztyn_2027_votes_processed",
            "results_url": "https://glosujobo.olsztyn.eu/wyniki",
        },
        "get_projects": {
            "data_dir": "2027",
            "excel_filename": "Olsztyn_2027_projects_processed",
            "columns_mapping": {
                "project_id": "project_id",
                "name": "name",
                "cost": "cost",
                "votes": "votes",
                "district": "district",
                "selected": "selected",
                "project_url": "project_url",
            },
        },
        "get_votes": {
            "data_dir": "2027",
            "excel_filename": "Olsztyn_2027_votes_processed",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "sex": "sex",
                "vote_column": "vote",
                "district": "district",
                "voting_method": "voting_method",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_no_points",
        },
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                "project_url",
            ],
            "districts_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                "project_url",
            ],
        },
        "votes_data": {
            "unit_fields": ["voter_id", "sex", "vote", "voting_method"],
            "districts_fields": ["voter_id", "sex", "vote", "voting_method"],
        },
        "metadata": {
            "vote_type": "approval",
            "rule": "greedy",
            "date_begin": "01.06.2026",
            "date_end": "21.06.2026",
            "min_length": "1",
            "max_length": "3",
            "edition": "13",
            "language": "pl",
            "currency": "PLN",
            "unit": {"max_length": "3"},
            "district": {"max_length": "3"},
            "district_comments": {
                district: [
                    f"Initially, the budget was {initial_budget:,} PLN. The rules allow unused funds to be allocated to the next highest-voted projects. After this reallocation, we adjusted the budget to {effective_budget:,} PLN."
                ]
                for district, initial_budget, effective_budget in (
                    ("Dajtki", 237185, 276000),
                    ("Generałów", 339332, 604832),
                    ("Jaroty", 557775, 1157775),
                    ("Nad Jez. Długim", 212198, 404198),
                    ("Nagórki", 320059, 430000),
                    ("Podgrodzie", 294074, 377000),
                    ("Podleśna", 329982, 404500),
                    ("Pojezierze", 314277, 390650),
                    ("Zatorze", 238013, 476026),
                )
            },
        },
    }
}
