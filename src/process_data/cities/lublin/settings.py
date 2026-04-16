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
                        "Lublin's citywide budget was split into two pools: 'hard' "
                        "for infrastructural projects and 'soft' for "
                        "non-infrastructural projects. "
                        "Each voter had two citywide votes and could use both on "
                        "'hard', both on 'soft', or split them between the two pools. "
                        "This hard/soft distinction was not indicated to voters during "
                        "voting and only mattered during tallying."
                    ),
                    (
                        "Initially, 6,900,000 PLN was allocated to citywide "
                        "projects, with 30% reserved for 'soft' projects "
                        "(2,070,000 PLN) and 70% for 'hard' projects "
                        "(4,830,000 PLN). After the district results were "
                        "finalized, the actual district allocation was "
                        "7,887,385 PLN, leaving 7,112,615 PLN for citywide "
                        "projects. The city then set the final citywide budgets "
                        "to 2,133,785 PLN for 'soft' projects and 4,978,830 PLN "
                        "for 'hard' projects."
                    ),
                    (
                        "Due to an error in the voting system, one citywide ballot "
                        "(voter_id 23819) was incorrectly merged into a single vote "
                        "with four citywide projects: two 'hard' and two 'soft', "
                        "instead of at most two citywide projects in total. The city "
                        "counted these indications, so for consistency with the "
                        "official project totals we also keep them in the dataset. "
                        "This did not affect the election outcome."
                    ),
                ]
            },
            "district": {},
            "currency": "PLN",
        },
    },
}
