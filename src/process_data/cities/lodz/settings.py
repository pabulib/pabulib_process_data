all_data = {
    2023: {
        "base_data": {
            "country": "Poland",
            "unit": "Łódź",
            "instance": 2023,
            "subdistricts": True,
        },
        "preprocess": {
            "excel_to_preprocess": "WYNIKI_XI_EDYCJI_LBO_publikacja",
            "data_dir": "2023",
            "output_excel_path": "Lodz_2023_projects_processed",
        },
        "get_projects": {
            "data_dir": "2023",
            "excel_filename": "Lodz_2023_projects_processed",
            "columns_mapping": {
                "project_id": "Id",
                "name": "Tytuł",
                "cost": "Kwota",
                "votes": "Głosów",
                "district": "district",
                "subdistrict": "subdistrict",
                "selected": "selected",
                "category": "Kategoria",
            },
        },
        "get_votes": {
            "excel_filename": "Glosowanie-Dane-XI ŁBO",
            "data_dir": "2023",
            "only_valid_votes": True,
            "district_name_mapping": True,
            "columns_mapping": {
                "voter_id": "IDWPIS",
                "sex": "PLEC",
                "age": "WIEK",
                "district": "REJON_ID",
                "subdistrict": "OSIEDLE_ID",
                "voting_method": "PAPIER/INTERNET",
                "vote_column": "PROJEKT_ID",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_no_points",
        },
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                "category",
            ]
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
            "districts_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
        },
        "metadata": {
            "vote_type": "approval",
            "rule": "greedy",
            "date_begin": "02.10.2023",
            "date_end": "31.10.2023",
            "language": "polish",
            "edition": "11",
            "currency": "PLN",
            "max_length": "5",
            "unit": {
                "comment": [
                    "Initially, the budget for the citywide projects was set at 7,000,000. However, due to regulations, unused funds from district PBs were reallocated to citywide projects. Consequently, the citywide budget was increased to 7,605,325."
                ]
            },
            "district": {
                # should be applied only for districts where it happend
                # "comment": [
                # "
                # Due to regulations mandating a minimum of 50 votes for funding, some projects were not selected even though there was some money left."
                # ]
            },
        },
    }
}
