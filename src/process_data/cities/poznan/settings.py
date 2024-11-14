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
            "vote_type": "choose-1",
            "rule": "greedy",
            "date_begin": "13.09.2023",
            "date_end": "27.09.2023",
            "language": "pl",
            "min_length": "1",
            "max_length": "1",
            "edition": "12",
            "currency": "PLN",
            "unit": {},
            "district": {},
            "subdistrict_sizes": True,
            "comment": [
                "The GreedySort works as follows: At the beginning, we sort projects based on the number of votes. Then, we fund projects that received the highest number of votes until the next project on the list does not fit within the budget. Finally, if the remaining budget is enough to fund at least 80% of that project, we fund it as well with the external reserve funds (for example, the unused funds remaining in other districts). We mark such project with number 2 in the selected column.",
                # only to one file with `3` as selected (1 - large)
                # "Sometimes, additional funds (for example, unused funds from other districts) are allocated to a district. These funds are used to finance the the highest-voted projects that have not yet been selected. We mark such projects with number 3 in the selected column."
            ],
        },
    }
}
