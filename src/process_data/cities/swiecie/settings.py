def make_year(instance, source_year, edition, date_begin, date_end):
    return {
        "base_data": {
            "country": "Poland",
            "unit": "Swiecie",
            "instance": instance,
        },
        "preprocess": {
            "data_dir": str(instance),
            "source_year": source_year,
            "date_end": date_end,
            "projects_excel": f"Swiecie_{instance}_projects_processed",
            "votes_excel": f"Swiecie_{instance}_votes_processed",
        },
        "get_projects": {
            "data_dir": str(instance),
            "excel_filename": f"Swiecie_{instance}_projects_processed",
            "columns_mapping": {
                "project_id": "project_id",
                "name": "name",
                "cost": "cost",
                "votes": "votes",
                "district": "district",
                "selected": "selected",
            },
        },
        "get_votes": {
            "excel_filename": f"Swiecie_{instance}_votes_processed",
            "data_dir": str(instance),
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "age": "age",
                "vote_column": "vote",
                "district": "district",
                "neighborhood": "neighborhood",
                "voting_method": "voting_method",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_no_points",
            "voter_id_integer": False,
        },
        "projects_data": {
            "unit_fields": ["project_id", "cost", "votes", "name", "selected"],
        },
        "votes_data": {
            "unit_fields": ["voter_id", "age", "vote", "neighborhood", "voting_method"],
        },
        "metadata": {
            "vote_type": "approval",
            "rule": "equalshares/add1",
            "date_begin": date_begin,
            "date_end": date_end,
            "edition": str(edition),
            "currency": "PLN",
        },
    }


all_data = {
    2024: make_year(2024, 2024, 4, "18.09.2023", "25.09.2023"),
    2025: make_year(2025, 2025, 5, "23.09.2024", "27.09.2024"),
    2026: make_year(2026, 2026, 6, "22.09.2025", "26.09.2025"),
}
