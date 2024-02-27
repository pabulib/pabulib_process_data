all_data = {
    2024: {
        "base_data": {
            "country": "Poland",
            "unit": "Poznań",
            "instance": 2024,
            "subdistricts": True,
        },
        "get_projects": {
            "data_dir": "2024",
            "excel_filename": "pbo-projekty-wyniki-20240216-projekty",
            "excel_ext": "xls",
            "columns_mapping": {
                "project_id": "Numer projektu",
                "name": "Nazwa projektu",
                "cost": "Koszt",
                "votes": "Liczba głosów",
                "district": "dzielnica",
                "subdistrict": "rodzaj",
                "selected": "czy wybrany",
            },
        },
        "get_votes": {
            "excel_filename": "pbo-projekty-wyniki-20240216-glosy",
            "excel_ext": "xls",
            "data_dir": "2024",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "vote_column": "vote",
            },
            "rows_iterator_handler": "no_points_votes_not_separated",
            "load_subdistricts_mapping": True,
        },
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
            ],
        },
        "votes_data": {
            "unit_fields": ["voter_id", "vote"],
            "districts_fields": ["voter_id", "vote"],
        },
        "metadata": {
            "vote_type": "ordinal",
            "rule": "greedy",
            "date_begin": "13.09.2023",
            "date_end": "27.09.2023",
            "language": "polish",
            "min_length": "1",
            "max_length": "1",
            "edition": "10",
            "currency": "PLN",
            "unit": {},
            "district": {},
        },
    }
}
