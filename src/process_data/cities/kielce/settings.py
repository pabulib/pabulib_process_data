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
            "additional_funded_project_ids": ["RE.05", "RE.50"],
            "project_cost_overrides": {
                "RE.43": 187350,
            },
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
                    "The city increased the citywide budget from 4,200,000 PLN to 4,672,275 PLN before final selection."
                ],
            },
            "district": {
                "rule": "greedy",
                "min_length": "0",
                "max_length": "2",
            },
            "district_metadata": {
                "Rejon 2": {
                    "comment": [
                        "RE.05 is marked with selected=2 because the official results include it as an additional project funded outside the regular regional pool."
                    ],
                },
                "Rejon 4": {
                    "comment": [
                        "RE.50 is marked with selected=2 because the official results include it as an additional project funded outside the regular regional pool."
                    ],
                },
                "Rejon 5": {
                    "comment": [
                        "Project RE.43 originally cost 205,660 PLN, but the city reduced its cost to 187,350 PLN under the local rule, which allowed the project to be funded."
                    ],
                },
            },
        },
    },
}
