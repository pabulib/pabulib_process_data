category_ii_large_districts = [
        "1000-LECIA",
        "BARANÓWKA",
        "BIAŁA",
        "BUDZIWÓJ",
        "DRABINIANKA",
        "DĄBROWSKIEGO",
        "GENERAŁA GROTA ROWECKIEGO",
        "GENERAŁA WŁADYSŁAWA ANDERSA",
        "KMITY",
        "KOTULI",
        "KRAKOWSKA-POŁUDNIE",
        "KRÓLA STANISŁAWA AUGUSTA",
        "MIESZKA I",
        "NOWE MIASTO",
        "PADEREWSKIEGO",
        "PIASTÓW",
        "POBITNO",
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

category_ii_small_districts = [
    "BZIANKA",
    "MATYSÓWKA",
    "MIŁOCIN",
    "MIŁOCIN - ŚW. HUBERTA",
    "POGWIZDÓW NOWY",
]

category_ii_budgets = {
    **{district: 400000 for district in category_ii_large_districts},
    **{district: 300000 for district in category_ii_small_districts},
}


budgets = {
    2026: {
        "Kategoria I": 2000000,
        "Kategoria III": 1000000,
        **category_ii_budgets,
    }
}
