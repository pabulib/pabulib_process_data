all_data = {
    2023: {
        "base_data": {
            "country": "Poland",
            "unit": "Kraków",
            "instance": 2023,
        },
        "get_projects": {
            "data_dir": "2023",
            "excel_filename": "ZbiórProjektówBO2023",
            "columns_mapping": {
                "project_id": "PROJEKT",
                "name": "TYTUL",
                "cost": "KOSZT",
                "score": "PUNKTY",
                "votes": "GLOSY",
                "district": "DZIELNICA",
                "category": "KATEGORIA",
                "selected": "STATUS",
            },
        },
        "get_votes": {
            "excel_filename": "ZbiórGłosówBO2023 v2",
            "data_dir": "2023",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "ID",
                "sex": "MALE",
                "age": "WIEK",
                "points": "LICZBA_PUNKTOW",
                "vote_column": "NR_PROJEKTU",
                "voting_method": "VTYPE",
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
            ]
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "sex", "vote", "neighborhood"],
            "districts_fields": ["voter_id", "age", "sex", "vote"],
        },
        "metadata": {
            "vote_type": "ordinal",
            "rule": "greedy",
            "date_begin": "13.09.2023",
            "date_end": "27.09.2023",
            "language": "polish",
            "min_length": "3",
            "max_length": "3",
            "edition": "10",
            "currency": "PLN",
            "unit": {},
            "district": {},
        },
    }
}
