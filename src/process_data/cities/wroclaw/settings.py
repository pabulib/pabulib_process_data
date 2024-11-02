all_data = {
    # 2024: {
    #     "base_data": {
    #         "country": "Poland",
    #         "unit": "Wrocław",
    #         "instance": 2024,
    #     },
    #     "get_projects": {"excel_filename": "wbo-2023-statystyki-do-open-data"},
    #     "get_votes": {
    #         "excel_filename": "wbo-lista-glosow-2023.csv",
    #         "csv_settings": {"delimiter": ";"},
    #         "only_valid_votes": True,
    #         "columns_mapping": {
    #             "voter_id": "Lp",
    #             "sex": "Plec",
    #             "age": "Wiek",
    #             "voting_method": "Zrodlo",
    #             "votes_columns": {
    #                 "unit": "Ponadosiedlowy",
    #                 "local": "Osiedlowy",
    #             },
    #         },
    #         "rows_iterator_handler": "one_voter_one_row_no_points",
    #         "valid_value": "",
    #     },
    #     "projects_data": {
    #         "unit_fields": [
    #             "project_id",
    #             "cost",
    #             "votes",
    #             "name",
    #             "selected",
    #             "category",
    #             "neighborhood",
    #         ]
    #     },
    #     "votes_data": {
    #         "unit_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
    #         "districts_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
    #     },
    #     "metadata": {
    #         "vote_type": "choose-1",
    #         "rule": "greedy",
    #         "date_begin": "22.09.2023",
    #         "date_end": "09.10.2023",
    #         "language": "polish",
    #         "min_length": "1",
    #         "max_length": "1",
    #         "edition": "11",
    #         "currency": "PLN",
    #         "unit": {},
    #         "district": {
    #             "description": "PB in Wrocław, projects of local significance"
    #         },
    #         "comment": [
    #             (
    #                 "Due to a system error, project 285 was mistakenly categorized "
    #                 "as a citywide before being accurately reclassified as a local"
    #                 " one. However, during this time, it had gathered 141 votes, "
    #                 "making it appear as though some voters had cast two votes "
    #                 "for local projects. We separated them by adding the prefix"
    #                 " 99999 to the voter_id, to be consistent with city results "
    #                 "and to avoid having incorrect (i.e., too long) votes."
    #             )
    #         ],
    #     },
    # },
    2023: {
        "base_data": {
            "country": "Poland",
            "unit": "Wrocław",
            "instance": 2023,
        },
        "get_projects": {"excel_filename": "wbo-2023-statystyki-do-open-data"},
        "get_votes": {
            "excel_filename": "wbo-lista-glosow-2023.csv",
            "csv_settings": {"delimiter": ";"},
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "Lp",
                "sex": "Plec",
                "age": "Wiek",
                "voting_method": "Zrodlo",
                "votes_columns": {
                    "unit": "Ponadosiedlowy",
                    "local": "Osiedlowy",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
            "valid_value": "",
        },
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                "category",
                "neighborhood",
            ]
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
            "districts_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
        },
        "metadata": {
            "vote_type": "choose-1",
            "rule": "greedy",
            "date_begin": "22.09.2023",
            "date_end": "09.10.2023",
            "language": "polish",
            "min_length": "1",
            "max_length": "1",
            "edition": "11",
            "currency": "PLN",
            "unit": {},
            "district": {
                "description": "PB in Wrocław, projects of local significance"
            },
            "comment": [
                (
                    "Due to a system error, project 285 was mistakenly categorized "
                    "as a citywide before being accurately reclassified as a local"
                    " one. However, during this time, it had gathered 141 votes, "
                    "making it appear as though some voters had cast two votes "
                    "for local projects. We separated them by adding the prefix"
                    " 99999 to the voter_id, to be consistent with city results "
                    "and to avoid having incorrect (i.e., too long) votes."
                )
            ],
        },
    },
    2022: {
        "base_data": {
            "country": "Poland",
            "unit": "Wrocław",
            "instance": 2022,
        },
        "get_projects": {},
        "get_votes": {
            "excel_filename": "wbo_lista_glosow_2022.csv",
            "csv_settings": {"delimiter": ";"},
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "Lp",
                "sex": "Plec",
                "age": "Wiek",
                "voting_method": "Zrodlo",
                "votes_columns": {
                    "unit": "Ponadosiedlowy",
                    "local": "Osiedlowy",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
            "valid_value": "",
        },
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                "category",
                "latitude",
                "longitude",
            ]
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
            "districts_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
        },
        "metadata": {
            "vote_type": "choose-1",
            "rule": "greedy",
            "date_begin": "23.09.2022",
            "date_end": "10.10.2022",
            "language": "polish",
            "min_length": "1",
            "max_length": "1",
            "edition": "10",
            "currency": "PLN",
            "comment": [
                (
                    "Due to an error in the voting system, there were 4 voters "
                    "with two local votes instead of one citywide and one local."
                    " The city counted them, so for the consistency of the "
                    "results, we moved these four votes from the citywide to the"
                    " local (added at the end with the prefix 11) and counted "
                    "them as proper votes."
                )
            ],
            "unit": {},
            "district": {
                "description": "PB in Wrocław, projects of local significance"
            },
        },
    },
}
