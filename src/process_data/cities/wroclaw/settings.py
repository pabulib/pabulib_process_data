all_data = {
    2022: {
        "base_data": {
            "country": "Poland",
            "unit": "Wrocław",
            "instance": 2022,
        },
        "get_projects": {},
        "get_votes": {
            "excel_filename": "wbo_lista_glosow_2022.csv",
            "csv_settings": {
                "delimiter": ";"
            },
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
            "only_valid_votes": True,
        },
        "projects_data": {
            "unit_fields": ["project_id", "cost", "votes", "name", "selected", "category", "latitude", "longitude"]
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
            "districts_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
        },
        "metadata": {
            "vote_type": "approval",
            "rule": "greedy",
            "date_begin": "23.09.2022",
            "date_end": "10.10.2022",
            "language": "polish",
            "min_length": "1",
            "max_length": "1",
            "edition": "10",
            "language": "polish",
            "comment": (
                "Due to an error in the voting system, there were 4 voters "
                "with two local votes instead of one citywide and one local."
                " The city counted them, so for the consistency of the "
                "results, we moved these four votes from the citywide to the"
                " local (added at the end with the prefix 11) and counted "
                "them as proper votes."),
            "unit": {},
            "district": {
                "description": "PB in Wrocław, projects of local significance"
            },
        },
    },
}
