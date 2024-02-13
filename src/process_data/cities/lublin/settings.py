all_data = {
    2020: {
        "base_data": {
            "country": "Poland",
            "unit": "Lublin",
            "instance": 2020,
        },
        "get_projects": {
            # "projects_docx": "lista_zlozonych_projektow_bo2020.pdf",
            # if already converted
            "projects_excel": "Lublin2020"
        },
        "get_votes": {
            "excel_filename": "Lublin2020.csv",
            "csv_settings": {"encoding": "ANSI"},
            "columns_mapping": {
                "voter_id": "ID głosującego",
                "sex": "Płeć słownie",
                "age": "Wiek",
                "voting_method": "Rodzaj głosowania słownie",
                # "if_valid": "",
                "district": "Dzielnica",
                "vote_column": "Nr projektu",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_no_points",
            "valid_value": "",
            "only_valid_votes": True,
        },
        "projects_data": {
            # "unit_fields": ["project_id", "cost", "votes", "name", "selected"]
            "unit_fields": ["project_id", "cost", "votes", "name"]
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "sex", "vote", "neighborhood"],
            "districts_fields": ["voter_id", "age", "sex", "vote"],
        },
        "metadata": {
            "vote_type": "approval",
            "rule": "greedy",
            "date_begin": "23.09.2019",
            "date_end": "07.10.2019",
            "language": "polish",
            "min_length": "1",
            "max_length": "2",
            "edition": "7",
            "unit": {},
            "district": {"description": "PB in Lublin, projects of local significance"},
            "currency": "PLN",
        },
    },
}
