all_data = {
    2026: {
        "base_data": {
            "country": "Poland",
            "unit": "Rybnik",
            "instance": 2026,
        },
        "preprocess": {
            "data_dir": "2026",
            "source_votes_excel": "zanonimizowane głosy BO Rybnik na 2026 r.",
            "projects_excel": "Rybnik_2026_projects_processed",
            "votes_excel": "Rybnik_2026_votes_processed",
            "results_url": "https://budzet-obywatelski.rybnik.eu/poprzednie-edycje/13/wyniki",
        },
        "get_projects": {
            "data_dir": "2026",
            "excel_filename": "Rybnik_2026_projects_processed",
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
            "excel_filename": "Rybnik_2026_votes_processed",
            "data_dir": "2026",
            "only_valid_votes": True,
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
            "rule": "greedy",
            "date_begin": "29.09.2025",
            "date_end": "05.10.2025",
            "language": "pl",
            "min_length": "1",
            "edition": "13",
            "currency": "PLN",
            "unit": {"max_length": "1"},
            "district": {
                "max_length": "1",
                "comment": [
                    "People could vote for any district project regardless of where they lived. So here district means a separate pool of projects and budget, not a local electorate.",
                ],
            },
        },
    },
}
