all_data = {
    2025: {
        "base_data": {
            "country": "Poland",
            "unit": "Gdynia",
            "instance": 2025,
            "subdistricts": True,
        },
        "preprocess": {
            "excel_filename": "bo2025-gosowanie",
            "data_dir": "2025",
            "city_projects_filename": "bo2025-projekty-miejskie",
            "district_projects_filename": "bo2025-projekty-dzielnicowe",
        },
        "get_projects": {
            "data_dir": "2025",
            "city_projects_filename": "bo2025-projekty-miejskie",
            "district_projects_filename": "bo2025-projekty-dzielnicowe",
            "results_pdf": "wyniki-glosowania",
        },
        "get_votes": {
            "excel_filename": "bo2025-gosowanie",
            "data_dir": "2025",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "ID_karty",
                "sex": "Plec",
                "age": "Wiek",
                "district": "Dzielnica",
                "votes_columns": {
                    "unit": "citywide_vote",
                    "small": "small_vote",
                    "large": "large_vote",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
            "valid_value": "",
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
            "rule": "greedy-no-skip",
            "date_begin": "01.09.2025",
            "date_end": "16.09.2025",
            "language": "pl",
            "min_length": "1",
            "max_length": "3",
            "edition": "12",
            "unit": {"min_project_score_threshold": 1000},
            "district": {"min_project_score_threshold": 50},
            "subdistricts": True,
            "subdistrict_sizes": True,
            "currency": "PLN",
        },
    },
    2024: {
        "base_data": {
            "country": "Poland",
            "unit": "Gdynia",
            "instance": 2024,
            "subdistricts": True,
        },
        "preprocess": {
            "excel_filename": "bo2024-gosowanie",
            "data_dir": "2024",
            "city_projects_filename": "bo2024-projekty-miejskie",
            "district_projects_filename": "bo2024-projekty-dzielnicowe",
        },
        "get_projects": {
            "data_dir": "2024",
            "city_projects_filename": "bo2024-projekty-miejskie",
            "district_projects_filename": "bo2024-projekty-dzielnicowe",
            "results_pdf": "wyniki-glosowania",
        },
        "get_votes": {
            "excel_filename": "bo2024-gosowanie",
            "data_dir": "2024",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "ID_karty",
                "sex": "Plec",
                "age": "Wiek",
                "district": "Dzielnica",
                "votes_columns": {
                    "unit": "citywide_vote",
                    "small": "small_vote",
                    "large": "large_vote",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
            "valid_value": "",
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
            "rule": "greedy-no-skip",
            "date_begin": "02.09.2024",
            "date_end": "16.09.2024",
            "language": "pl",
            "min_length": "1",
            "max_length": "3",
            "edition": "11",
            "unit": {"min_project_score_threshold": 1000},
            "district": {"min_project_score_threshold": 50},
            "subdistricts": True,
            "subdistrict_sizes": True,
            "currency": "PLN",
        },
    },
    2023: {
        "base_data": {
            "country": "Poland",
            "unit": "Gdynia",
            "instance": 2023,
            "subdistricts": True,
        },
        "preprocess": {
            "excel_filename": "bo-2023-gosowanie",
            "data_dir": "2023",
            "city_projects_filename": "bo-2023-projekty-miejskie",
            "district_projects_filename": "bo-2023-projekty-dzielnicowe",
        },
        "get_projects": {
            "data_dir": "2023",
            "city_projects_filename": "bo-2023-projekty-miejskie",
            "district_projects_filename": "bo-2023-projekty-dzielnicowe",
            "results_pdf": "wyniki-glosowania",
        },
        "get_votes": {
            "excel_filename": "bo-2023-gosowanie",
            "data_dir": "2023",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "ID_karty",
                "sex": "Plec",
                "age": "Wiek",
                "district": "Dzielnica",
                "votes_columns": {
                    "unit": "citywide_vote",
                    "small": "small_vote",
                    "large": "large_vote",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
            "valid_value": "",
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
            "rule": "greedy-no-skip",
            "date_begin": "04.09.2023",
            "date_end": "19.09.2023",
            "language": "pl",
            "min_length": "1",
            "max_length": "3",
            "edition": "10",
            "unit": {"min_project_score_threshold": 1000},
            "district": {"min_project_score_threshold": 50},
            "subdistricts": True,
            "subdistrict_sizes": True,
            "currency": "PLN",
        },
    },
    2022: {
        "base_data": {
            "country": "Poland",
            "unit": "Gdynia",
            "instance": 2022,
            "subdistricts": True,
        },
        "preprocess": {
            "excel_filename": "bo_glosowanie_2022",
            "data_dir": "2022",
            "city_projects_filename": "bo_2022_projekty_miejskie",
            "district_projects_filename": "bo_2022_projekty_dzielnicowe",
        },
        "get_projects": {
            "data_dir": "2022",
            "city_projects_filename": "bo_2022_projekty_miejskie",
            "district_projects_filename": "bo_2022_projekty_dzielnicowe",
            "results_pdf": "wyniki-glosowania",
        },
        "get_votes": {
            "excel_filename": "bo_glosowanie_2022",
            "data_dir": "2022",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "ID_karty",
                "sex": "Plec",
                "age": "Wiek",
                "district": "Dzielnica",
                "votes_columns": {
                    "unit": "citywide_vote",
                    "small": "small_vote",
                    "large": "large_vote",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
            "valid_value": "",
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
            "rule": "greedy-no-skip",
            "date_begin": "05.09.2022",
            "date_end": "19.09.2022",
            "language": "pl",
            "min_length": "1",
            "max_length": "3",
            "edition": "9",
            "unit": {"min_project_score_threshold": 1000},
            "district": {"min_project_score_threshold": 50},
            "subdistricts": True,
            "subdistrict_sizes": True,
            "currency": "PLN",
        },
    },
    2021: {
        "base_data": {
            "country": "Poland",
            "unit": "Gdynia",
            "instance": 2021,
            "subdistricts": True,
        },
        "preprocess": {
            "excel_filename": "bo_2021_glosowanie",
            "data_dir": "2021",
            "city_projects_filename": "bo_2021_projekty_miejskie",
            "district_projects_filename": "bo_2021_projekty_dzielnicowe",
        },
        "get_projects": {
            "data_dir": "2021",
            "city_projects_filename": "bo_2021_projekty_miejskie",
            "district_projects_filename": "bo_2021_projekty_dzielnicowe",
            "results_pdf": "wyniki-glosowania_wszystkie-projekty_na-strone",
        },
        "get_votes": {
            "excel_filename": "bo_2021_glosowanie",
            "data_dir": "2021",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "sex": "plec",
                "age": "wiek",
                "district": "dzielnica",
                "votes_columns": {
                    "unit": "citywide_vote",
                    "small": "small_vote",
                    "large": "large_vote",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
            "valid_value": "",
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
            "rule": "greedy-no-skip",
            "date_begin": "07.06.2021",
            "date_end": "21.06.2021",
            "language": "pl",
            "min_length": "1",
            "max_length": "3",
            "edition": "8",
            "unit": {"min_project_score_threshold": 1000},
            "district": {"min_project_score_threshold": 50},
            "subdistricts": True,
            "subdistrict_sizes": True,
            "currency": "PLN",
        },
    },
    2020: {
        "base_data": {
            "country": "Poland",
            "unit": "Gdynia",
            "instance": 2020,
            "subdistricts": True,
        },
        "get_projects": {
            # VOTES WERE MISCOUNTED BY THE COMPANY RESPONSIBLE FOR A VOTING
            # SO AN UPDATE IN RESULTS WAS NEEDED:
            # https://bo.gdynia.pl/2020/09/16/oswiadczenie-dotyczace-zmian-wynikow-glosowania-w-bo-2020/
            # TWO PROJECTS WERE FUNDED ADDITIONALY BY THE COMPANY
            # ALSO, CITY FUNDED COUPLE OF PROJECTS FROM DIFFERENT BUDZETS
            # (THANKS TO LARGE ATTENDANCE FOR EXAMPLE)
            # WE MARKED BOTH CASES AS selected: 2
            "data_dir": "2020",
            # "projects_docx": "2020-06-23 wyniki głosowania.pdf",
            # if already converted without .pdf
            "projects_docx": "2020-06-23 wyniki głosowania",
            "columns": {
                # 'Poziom': "is_citywide",
                "Numer na liście": "project_id",  # "Numer"
                # 'ID projektu': "project_id",
                "Tytuł": "name",
                "Koszt": "cost",
                "Liczba punktów": "votes",  # "Aktualna liczba głosów"
                "Zwycięski": "selected",  # "Czy zwycięski"
            },
            "cell_colours": {"district": "b4c5e7", "size": "ddebf7"},
            # "cell_colours": {"district": "ff9900", "size": "e0e0e0"},
        },
        "get_votes": {
            "excel_filename": "głosowanie _ BO2020",
            "data_dir": "2020",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "Lp.",
                "sex": "Płeć",
                "age": "Wiek",
                "district": "Dzielnica w której wybrano projekty",
                "votes_columns": {
                    "unit": "Wybrane projekty ogólnomiejskie",
                    "small": "Wybrane projekty małe",
                    "large": "Wybrane projekty duże",
                },
            },
            "district_name_mapping": True,
            "rows_iterator_handler": "one_voter_one_row_no_points",
            "valid_value": "ważna",
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
            "date_begin": "08.06.2020",
            "date_end": "22.06.2020",
            "language": "pl",
            "min_length": "1",
            "max_length": "3",
            "edition": "7",
            "unit": {},
            "district": {},
            "subdistricts": True,
            "subdistrict_sizes": True,
            "currency": "PLN",
        },
    },
}
