small_comment = [
    "Unused funds from the three budget categories were pooled to fund additional highest-scoring projects. Project 32 is marked with selected=2."
]

medium_comment = [
    "Unused funds from the three budget categories were pooled to fund additional highest-scoring projects. Projects 114 and 124 are marked with selected=2."
]

all_data = {
    2026: {
        "base_data": {
            "country": "Poland",
            "unit": "Radom",
            "instance": 2026,
        },
        "preprocess": {
            "data_dir": "2026",
            "source_excel": "BO 2026 - punkty",
            "winners_docx": "radom_winners_2026",
            "projects_excel": "Radom_2026_projects_processed",
            "votes_excel": "Radom_2026_votes_processed",
        },
        "get_projects": {
            "data_dir": "2026",
            "excel_filename": "Radom_2026_projects_processed",
            "only_score_column": True,
            "columns_mapping": {
                "project_id": "project_id",
                "name": "name",
                "cost": "cost",
                "votes": "score",
                "district": "district",
                "selected": "selected",
                "neighborhood": "neighborhood",
            },
        },
        "get_votes": {
            "excel_filename": "Radom_2026_votes_processed",
            "data_dir": "2026",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "vote_column": "vote",
                "points": "points",
                "district": "district",
                "voting_method": "voting_method",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_with_points",
        },
        "projects_data": {
            "output_file_name_mapping": {
                "SMALL": "SMALL",
                "MEDIUM": "MEDIUM",
                "LARGE": "LARGE",
            },
            "unit_fields": [
                "project_id",
                "cost",
                "score",
                "name",
                "selected",
                "neighborhood",
            ],
        },
        "votes_data": {
            "output_file_name_mapping": {
                "SMALL": "SMALL",
                "MEDIUM": "MEDIUM",
                "LARGE": "LARGE",
            },
            "unit_fields": ["voter_id", "vote", "points", "voting_method"],
        },
        "metadata": {
            "output_file_name_mapping": {
                "SMALL": "SMALL",
                "MEDIUM": "MEDIUM",
                "LARGE": "LARGE",
            },
            "vote_type": "cumulative",
            "rule": "greedy",
            "date_begin": "21.06.2025",
            "date_end": "07.07.2025",
            "min_points": "1",
            "max_points": "3",
            "min_sum_points": "1",
            "max_sum_points": "3",
            "edition": "13",
            "language": "pl",
            "currency": "PLN",
            "district": {
                "comment": [
                    "The city does not store ballot-level data. VOTES contain one synthetic row for each project-point entry, so voter_id identifies an entry, not a person or ballot."
                ],
            },
            "district_metadata": {
                "small": {
                    "description": "Municipal PB in Radom, projects up to 100,000 PLN",
                    "remove_fields": ["district"],
                    "subunit": "projects up to 100,000 PLN",
                    "comment": small_comment,
                },
                "medium": {
                    "description": "Municipal PB in Radom, projects from 100,000 to 600,000 PLN",
                    "remove_fields": ["district"],
                    "subunit": "projects from 100,000 to 600,000 PLN",
                    "comment": medium_comment,
                },
                "large": {
                    "description": "Municipal PB in Radom, projects above 600,000 PLN",
                    "remove_fields": ["district"],
                    "subunit": "projects above 600,000 PLN",
                },
            },
        },
    },
}
