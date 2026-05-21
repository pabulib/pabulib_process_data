all_data = {
    2026: {
        "base_data": {
            "country": "Poland",
            "unit": "Kielce",
            "instance": 2026,
        },
        "preprocess": {
            "data_dir": "2026",
            "source_votes_excel": "Kopia KBO_2026 udip",
            "projects_excel": "Kielce_2026_projects_processed",
            "votes_excel": "Kielce_2026_votes_processed",
            "projects_url": "https://bo.kielce.eu/dopuszczone-wszystkie-2025-archiwum.html",
            "additional_funded_project_ids": ["OG.09", "RE.05", "RE.50", "RE.43"],
        },
        "get_projects": {
            "data_dir": "2026",
            "excel_filename": "Kielce_2026_projects_processed",
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
            "excel_filename": "Kielce_2026_votes_processed",
            "data_dir": "2026",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
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
            "unit_fields": ["voter_id", "age", "vote", "voting_method"],
            "districts_fields": ["voter_id", "age", "vote", "voting_method"],
        },
        "metadata": {
            "vote_type": "approval",
            "rule": "greedy",
            "date_begin": "24.09.2025",
            "date_end": "07.10.2025",
            "language": "pl",
            "edition": "13",
            "currency": "PLN",
            "unit": {
                "vote_type": "choose-1",
                "rule": "greedy-no-skip",
                "min_length": "1",
                "max_length": "1",
                "comment": [
                    "The official results include projects whose full verified costs exceeded the regular KBO budget. The city announced additional funds to implement them fully. We mark these projects with selected=2."
                ],
            },
            "district": {
                "rule": "greedy-no-skip",
                "min_length": "0",
                "max_length": "2",
                "comment": [
                    "The official results include projects whose full verified costs exceeded the regular KBO budget. Rejon 2 also received a turnout bonus project. We mark these projects with selected=2."
                ],
            },
        },
    },
}
