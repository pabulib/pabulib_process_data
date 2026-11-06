output_file_name_mapping = {
    "OSIEDLOWE": "LOCAL",
    "SZKOLNE": "SCHOOL",
}


all_data = {
    2027: {
        "base_data": {
            "country": "Poland",
            "unit": "Bialystok",
            "instance": 2027,
        },
        "preprocess": {
            "data_dir": "2027",
            "source_projects_docx": "bo2027_listy_rankingowe",
            "source_votes_excel": "bo2027_glosy",
            "projects_excel": "Bialystok_2027_projects_processed",
            "votes_excel": "Bialystok_2027_votes_processed",
            "expected_projects": 72,
            "expected_selected_by_pool": {
                "CITYWIDE": 23,
                "Osiedlowe": 8,
                "Szkolne": 2,
            },
            "expected_valid_ballots": 28448,
            "expected_valid_indications": 83269,
            "project_metadata_source": "official_projects_results",
            "project_vote_totals_reference_source": "official_projects_results",
            "votes_source": "anonymized_ballots",
            "require_matching_project_vote_totals": True,
            "project_totals_output_source": (
                "valid_ballots_after_matching_official_results"
            ),
        },
        "get_projects": {
            "data_dir": "2027",
            "excel_filename": "Bialystok_2027_projects_processed",
            "columns_mapping": {
                "project_id": "project_id",
                "name": "name",
                "cost": "cost",
                "votes": "votes",
                "district": "district",
                "neighborhood": "neighborhood",
                "selected": "selected",
            },
        },
        "get_votes": {
            "data_dir": "2027",
            "excel_filename": "Bialystok_2027_votes_processed",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "vote_column": "vote",
                "district": "district",
                "age": "age",
                "sex": "sex",
                "voting_method": "voting_method",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_no_points",
        },
        "projects_data": {
            "output_file_name_mapping": output_file_name_mapping,
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
                "neighborhood",
            ],
            "districts_fields_overrides": {
                "Szkolne": [
                    "project_id",
                    "cost",
                    "votes",
                    "name",
                    "selected",
                ]
            },
        },
        "votes_data": {
            "output_file_name_mapping": output_file_name_mapping,
            "unit_fields": [
                "voter_id",
                "vote",
                "age",
                "sex",
                "voting_method",
            ],
            "districts_fields": [
                "voter_id",
                "vote",
                "age",
                "sex",
                "voting_method",
            ],
        },
        "metadata": {
            "output_file_name_mapping": output_file_name_mapping,
            "vote_type": "approval",
            "rule": "greedy",
            "date_begin": "24.09.2026",
            "date_end": "07.10.2026",
            "min_length": "1",
            "max_length": "4",
            "edition": "14",
            "language": "pl",
            "currency": "PLN",
            "comment": [
                "The voter-age metadata contains very low values, starting "
                "from zero. Residents of all ages could vote, while minors "
                "required the consent of a parent or legal guardian."
            ],
            "district_metadata": {
                "Osiedlowe": {
                    "description": "Municipal PB in Białystok, Local Projects",
                    "remove_fields": ["district"],
                    "subunit": "Local Projects",
                },
                "Szkolne": {
                    "description": "Municipal PB in Białystok, School Projects",
                    "remove_fields": ["district"],
                    "subunit": "School Projects",
                },
            },
        },
    }
}
