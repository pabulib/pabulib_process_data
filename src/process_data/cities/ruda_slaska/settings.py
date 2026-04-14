all_data = {
    2026: {
        "base_data": {
            "country": "Poland",
            "unit": "Ruda_Slaska",
            "instance": 2026,
        },
        "preprocess": {
            "source_excel": "Ruda_Slaska_2026",
            "votes_source_excel": "UJ_dane_niewazne_glosy",
            "data_dir": "2026",
            "projects_excel": "Ruda_Slaska_2026_projects_processed",
            "votes_excel": "Ruda_Slaska_2026_votes_processed",
        },
        "get_projects": {
            "data_dir": "2026",
            "excel_filename": "Ruda_Slaska_2026_projects_processed",
            # Keep official project-level totals from the projects sheet.
            # Votes are still parsed from the anonymized ballots sheet.
            "preserve_official_results": True,
            "columns_mapping": {
                "project_id": "project_id",
                "name": "name",
                "cost": "cost",
                "votes": "votes",
                "score": "score",
                "district": "district",
                "selected": "selected",
                "category": "category",
                "neighborhood": "neighborhood",
            },
        },
        "get_votes": {
            "excel_filename": "Ruda_Slaska_2026_votes_processed",
            "data_dir": "2026",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "sex": "sex",
                "points": "points",
                "vote_column": "vote",
                "district": "district",
                "voting_method": "voting_method",
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
                "category",
                "neighborhood",
            ],
            "districts_fields": [
                "project_id",
                "cost",
                "votes",
                "score",
                "name",
                "selected",
                "category",
                "neighborhood",
            ],
        },
        "votes_data": {
            "unit_fields": ["voter_id", "sex", "vote", "points", "voting_method"],
            "districts_fields": ["voter_id", "sex", "vote", "points", "voting_method"],
        },
        "metadata": {
            # Semantically this is ordinal voting: voters rank up to 4 projects
            # in each pool, and the city derives points 4/3/2/1 from positions.
            # We still keep per-vote `points` in VOTES because current tooling
            # does not support an explicit scoring_fn metadata field yet.
            # Official city source for BO 2026 calls it the 13th edition.
            "vote_type": "ordinal",
            "rule": "greedy-exclusive",
            "date_begin": "08.09.2025",
            "date_end": "21.09.2025",
            "language": "pl",
            "min_length": "1",
            "max_length": "4",
            "edition": "13",
            "min_project_score_threshold": "30",
            "currency": "PLN",
            "unit": {},
            "district": {
                "comment": [
                    "In the municipal small-project pool, projects 12 and 26 were treated by the city as mutually exclusive because they concern the same area. Project 12 was funded and project 26 was excluded because project 12 received the higher score.",
                    "For Ruda Slaska 2026, the small-project pool was initially 4,100,000 PLN and the large-project pool was 1,681,585 PLN. When the remaining amount in one pool was not enough for the next project of that type, the unused funds from both pools were combined and used to fund the next feasible project by score. Therefore, the effective budget recorded for the municipal small pool is 4,411,585 PLN.",
                ]
            },
        },
    },
}
