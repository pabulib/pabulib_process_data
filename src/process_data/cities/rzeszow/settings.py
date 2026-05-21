accepted_project_ids_2026 = [
    5,
    18,
    22,
    19,
    24,
    26,
    27,
    28,
    29,
    34,
    35,
    40,
    37,
    38,
    39,
    42,
    44,
    47,
    49,
    51,
    52,
    53,
    54,
    55,
    58,
    60,
    63,
    62,
    65,
    68,
    71,
    79,
    75,
    77,
    80,
    84,
    87,
    89,
    92,
    94,
    95,
    96,
    98,
    147,
    132,
    161,
    130,
    106,
    120,
    124,
    128,
    135,
    104,
    115,
    108,
    137,
    118,
    151,
    103,
    105,
    110,
    131,
    134,
]

category_ii_districts = [
    "1000-LECIA",
    "BARANÓWKA",
    "BIAŁA",
    "BUDZIWÓJ",
    "BZIANKA",
    "DRABINIANKA",
    "DĄBROWSKIEGO",
    "GENERAŁA GROTA ROWECKIEGO",
    "GENERAŁA WŁADYSŁAWA ANDERSA",
    "KMITY",
    "KOTULI",
    "KRAKOWSKA-POŁUDNIE",
    "KRÓLA STANISŁAWA AUGUSTA",
    "MATYSÓWKA",
    "MIESZKA I",
    "MIŁOCIN",
    "MIŁOCIN - ŚW. HUBERTA",
    "NOWE MIASTO",
    "PADEREWSKIEGO",
    "PIASTÓW",
    "POBITNO",
    "POGWIZDÓW NOWY",
    "PRZYBYSZÓWKA",
    "PUŁASKIEGO",
    "STAROMIEŚCIE",
    "STARONIWA",
    "SŁOCINA",
    "WILKOWYJA",
    "ZALESIE",
    "ZAWISZY CZARNEGO",
    "ZAŁĘŻE",
    "ZWIĘCZYCA",
    "ŚRÓDMIEŚCIE",
]

category_ii_comment = (
    "District projects cover the construction, modernization, or renovation of "
    "neighborhood infrastructure. They are split into neighborhood files because "
    "the official rule applies a separate neighborhood budget cap: 300,000 PLN "
    "for neighborhoods with up to 2,000 registered residents and 400,000 PLN for "
    "neighborhoods above 2,000 registered residents."
)

category_ii_metadata = {
    district: {
        "description": f"District PB in Rzeszów, {district.title()}",
        "district": district.title(),
        "subunit": district.title(),
    }
    for district in category_ii_districts
}


all_data = {
    2026: {
        "base_data": {
            "country": "Poland",
            "unit": "Rzeszow",
            "instance": 2026,
        },
        "preprocess": {
            "data_dir": "2026",
            "source_projects_excel": "lista_projektow",
            "source_votes_excel": "lista_glosujacych",
            "projects_excel": "Rzeszow_2026_projects_processed",
            "votes_excel": "Rzeszow_2026_votes_processed",
            "accepted_project_ids": accepted_project_ids_2026,
        },
        "get_projects": {
            "data_dir": "2026",
            "excel_filename": "Rzeszow_2026_projects_processed",
            "columns_mapping": {
                "project_id": "project_id",
                "name": "name",
                "cost": "cost",
                "votes": "votes",
                "district": "district",
                "neighborhood": "neighborhood",
                "selected": "selected",
            },
        },
        "get_votes": {
            "excel_filename": "Rzeszow_2026_votes_processed",
            "data_dir": "2026",
            "only_valid_votes": True,
            "columns_mapping": {
                "voter_id": "voter_id",
                "vote_column": "vote",
                "district": "district",
                "voting_method": "voting_method",
            },
            "rows_iterator_handler": "one_voter_multiple_rows_no_points",
        },
        "projects_data": {
            "output_file_name_mapping": {
                "KATEGORIA_I": "",
                "KATEGORIA_III": "SOCIAL_ACTIVITIES",
            },
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                "neighborhood",
            ],
            "districts_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                "neighborhood",
            ],
            "districts_fields_overrides": {
                "Kategoria I": ["project_id", "cost", "votes", "name", "selected"],
                **{
                    district: ["project_id", "cost", "votes", "name", "selected"]
                    for district in category_ii_districts
                },
            },
        },
        "votes_data": {
            "output_file_name_mapping": {
                "KATEGORIA_I": "",
                "KATEGORIA_III": "SOCIAL_ACTIVITIES",
            },
            "unit_fields": ["voter_id", "vote", "voting_method"],
            "districts_fields": ["voter_id", "vote", "voting_method"],
        },
        "metadata": {
            "output_file_name_mapping": {
                "KATEGORIA_I": "",
                "KATEGORIA_III": "SOCIAL_ACTIVITIES",
            },
            "vote_type": "choose-1",
            "rule": "greedy",
            "date_begin": "21.05.2025",
            "date_end": "04.06.2025",
            "language": "pl",
            "min_length": "1",
            "max_length": "1",
            "edition": "13",
            "currency": "PLN",
            "district_display_names": {
                "Kategoria I": "Kategoria I",
                "Kategoria III": "Kategoria III",
            },
            "district_descriptions": {
                "Kategoria I": "Municipal PB in Rzeszów",
                "Kategoria III": "Municipal PB in Rzeszów, Social Activities Budget",
            },
            "district_metadata": {
                "Kategoria I": {"remove_fields": ["district", "subunit"]},
                "Kategoria III": {
                    "remove_fields": ["district"],
                    "subunit": "Social Activities Budget",
                },
                **category_ii_metadata,
            },
            "district_comments": {
                **{district: [category_ii_comment] for district in category_ii_districts},
                "GENERAŁA GROTA ROWECKIEGO": [
                    category_ii_comment,
                    "Project 36 was present in the voting list and received 94 valid ballot indications, but it was missing from the official project results provided by the city. Its project metadata was taken from the voting list and its vote total was counted from the ballots.",
                ],
            },
        },
    },
}
