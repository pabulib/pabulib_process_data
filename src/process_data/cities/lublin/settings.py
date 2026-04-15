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
            "projects_excel": "Lublin2020",
            "data_dir": "2020",
            "csv_settings": {"encoding": "cp1250"},
        },
        "get_votes": {
            "excel_filename": "Lublin2020.csv",
            "data_dir": "2020",
            "csv_settings": {"encoding": "cp1250"},
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
            "unit_fields": ["project_id", "cost", "votes", "name", "selected"]
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
            "language": "pl",
            "min_length": "1",
            "max_length": "2",
            "edition": "6",
            "unit": {
                "comment": [
                    (
                        "The initial citywide budgets were 4,830,000 PLN for "
                        "infrastructural ('hard') projects and 2,070,000 PLN for "
                        "non-infrastructural ('soft') projects. Unused funds from the "
                        "district pools were later added to these citywide pools."
                    ),
                    (
                        "Due to an error in the voting system, one citywide ballot "
                        "(voter_id 23819) was incorrectly merged into a single vote with "
                        "four citywide projects instead of at most two. The city counted "
                        "these indications, so for consistency with the official project "
                        "totals we split this ballot into two citywide votes and marked "
                        "the second one with the prefix 9999. This did not affect the "
                        "election outcome."
                    ),
                ]
            },
            "district": {},
            "currency": "PLN",
        },
    },
}
