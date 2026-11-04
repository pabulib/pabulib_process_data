all_data = {
    2027: {
        "base_data": {
            "country": "Poland",
            "unit": "Zabrze",
            "instance": 2027,
        },
        "preprocess": {
            "data_dir": "2027",
            "source_excel": "ZBP2027_glosowanie_a_fl",
            "projects_excel": "Zabrze_2027_projects_processed",
            "votes_excel": "Zabrze_2027_votes_processed",
        },
        "get_projects": {
            "data_dir": "2027",
            "excel_filename": "Zabrze_2027_projects_processed",
            # Keep the official project-level totals from the projects sheet.
            # The anonymized ballots are parsed independently and reconciled.
            "preserve_official_results": True,
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
            "data_dir": "2027",
            "excel_filename": "Zabrze_2027_votes_processed",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "vote_column": "vote",
                "district": "district",
                "neighborhood": "neighborhood",
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
            ],
            "districts_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
            ],
        },
        "votes_data": {
            "unit_fields": [
                "voter_id",
                "vote",
                "neighborhood",
                "voting_method",
            ],
            "districts_fields": [
                "voter_id",
                "vote",
                "neighborhood",
                "voting_method",
            ],
        },
        "metadata": {
            "vote_type": "choose-1",
            "rule": "greedy-threshold",
            "date_begin": "08.09.2026",
            "date_end": "25.09.2026",
            "min_length": "1",
            "max_length": "1",
            "edition": "13",
            "language": "pl",
            "currency": "PLN",
            "unit": {"min_project_score_threshold": "50"},
            "district": {"min_project_score_threshold": "50"},
            "district_comments": {
                "Centrum Południe": [
                    "Unused funds from all pools funded project P0029 as an attendance bonus. It is marked with selected=2."
                ],
                "Grzybowice": [
                    "Unused funds from all pools funded project P0011 as an attendance bonus. It is marked with selected=2."
                ],
                "Mikulczyce": [
                    "Ballot 20010 listed two local projects from different districts. To keep the data internally consistent, we split it into two votes, one in each district file. This did not affect the official result."
                ],
                "Skłodowskiej-Curie": [
                    "Ballot 20010 listed two local projects from different districts. To keep the data internally consistent, we split it into two votes, one in each district file. This did not affect the official result."
                ],
                "Śródmieście": [
                    "Unused funds from all pools funded projects P0030 and P0037 as attendance bonuses. They are marked with selected=2."
                ],
            },
        },
    }
}
