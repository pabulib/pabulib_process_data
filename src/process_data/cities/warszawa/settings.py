all_data = {
    2024: {
        "base_data": {
            "country": "Poland",
            "unit": "Warszawa",
            "instance": 2024,
        },
        "get_projects": {
            "data_dir": "2024",
            "excel_filename": "projekty_BO2024_PBL",
            "columns_mapping": {
                "project_id": "Numer projektu",
                "name": "Tytuł",
                "cost": "Koszt",
                "votes": "Liczba głosów ważnych",
                "district": "Dzielnica",
                "selected": "Status",
                # "category": "multiple category & target columns",
            },
        },
        "get_votes": {
            "excel_filename": "Karty-do-glosowania_BO2024_PBL",
            "data_dir": "2024",
            "only_valid_votes": False,
            "valid_value": "ważny",
            "columns_mapping": {
                "voter_id": "ID karty",
                "sex": "Płeć",
                "age": "Wiek",
                "district": "Dzielnica",
                "voting_method": "Sposób głosowania",
                "if_valid": "Status karty do głosowania",
                "votes_columns": {
                    "unit": "Numery projektów ogólnomiejskich",
                    "local": "Numery projektów dzielnicowych",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
        },
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                "category",
                "target",
            ]
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "sex", "vote", "neighborhood"],
            "districts_fields": ["voter_id", "age", "sex", "vote"],
        },
        "metadata": {
            "vote_type": "approval",
            "rule": "greedy",
            "date_begin": "15.06.2023",
            "date_end": "30.06.2023",
            "language": "polish",
            "edition": "10",
            "currency": "PLN",
            "unit": {"max_length": "10"},
            "district": {"max_length": "15"},
            "comment": "The metadata regarding the age of voters shows very low values (starting from zero), indicating that one doesn't need to be an adult to vote: If a voter is under 13, they can vote with the consent of a parent or guardian. Hence, for example, age 0 likely corresponds to cases where parents/guardians are voting on behalf of their children.",
        },
    }
}
