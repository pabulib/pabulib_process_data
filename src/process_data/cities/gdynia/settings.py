all_data = {
    2020: {
        "base_data": {
            "country": "Poland",
            "unit": "Gdynia",
            "instance": 2020,
            "subdistricts": True,
        },
        "get_projects": {
            # COMPANY THAT WAS RESPONSIBLE FOR A SYSTEM COUNTED VOTES WRONG
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
        "excel_data": {
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
            "language": "polish",
            "min_length": "1",
            "max_length": "3",
            "edition": "7",
            "language": "polish",
            "unit": {},
            "district": {},
            "subdistricts": True,
            "subdistrict_sizes": True
        },
    },
}
