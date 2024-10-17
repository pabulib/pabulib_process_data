all_data = {
    2023: {
        "base_data": {
            "country": "Poland",
            "unit": "Katowice",
            "instance": 2023,
        },
        "get_projects": {
            "data_dir": "2023",
            "excel_filename": "BO Katowice 2023 - gLosowanie",
            "columns_mapping": {
                "project_id": "NR ID",
                "name": "TYTUŁ ZADANIA",
                "cost": "KOSZT ZADANIA",
                # Only score column. Handle as votes and save it as score later
                "votes": "LICZBA UZYSKANYCH GŁOSÓW",
                # "votes": "",
                "district": "DZIELNICA",  # Added manually (VLOOKUP in Excel) from votes sheet
                "category": "KATEGORIA PROJEKTU",
                "selected": "WYBRANE / NIEWYBRANE W GŁOSOWANIU",
            },
            "only_score_column": True,
        },
        "get_votes": {
            "excel_filename": "BO Katowice 2023",
            "data_dir": "2023",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "IDWPIS",
                "sex": "PLEC",
                "age": "WIEK",
                "points": "GLOSOW",
                "vote_column": "ID",
                "district": "NAZWA DZIELNICY",
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
            "unit_fields": ["voter_id", "age", "sex", "vote", "points", "neighborhood"],
            "districts_fields": ["voter_id", "age", "sex", "vote", "points"],
        },
        "metadata": {
            "vote_type": "cumulative",
            "rule": "greedy",
            "date_begin": "11.09.2023",
            "date_end": "24.09.2023",
            "language": "polish",
            "min_length": "1",
            "max_length": "3",
            "edition": "10",
            "currency": "PLN",
            "unit": {},
            "district": {},
        },
    }
}
