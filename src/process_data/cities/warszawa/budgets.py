budgets = {
    # https://um.warszawa.pl/documents/57254/116699425/Raport+z+przeprowadzenia+11.+edycji+bud%C5%BCetu+obywatelskiego.pdf/1af9e37d-ba78-81dc-baf1-cc086f4be472?t=1726060016317
    2025: {
        "CITYWIDE": 31734758,
        "BEMOWO": 5077561,
        "BIALOLEKA": 4971779,
        "BIELANY": 5500692,
        "MOKOTOW": 9097298,
        "OCHOTA": 3490823,
        "PRAGA-POLNOC": 2750346,
        "PRAGA-POLUDNIE": 7510560,
        "REMBERTOW": 1057825,
        "SRODMIESCIE": 4865996,
        "TARGOWEK": 5183344,
        "URSUS": 2538781,
        "URSYNOW": 6346952,
        "WAWER": 3173476,
        "WESOLA": 1057825,
        "WILANOW": 1586738,
        "WLOCHY": 1798303,
        "WOLA": 5923822,
        "ZOLIBORZ": 2115651,
    },
    # https://um.warszawa.pl/waw/bo/-/harmonogram-i-kwoty-10-edycja
    2024: {
        "CITYWIDE": 30428140,
        "BIELANY": 5274211,
        "BIALOLEKA": 4767075,
        "URSYNOW": 6085628,
        "URSUS": 2434251,
        "TARGOWEK": 4969929,
        "BEMOWO": 4868502,
        "PRAGA-POLUDNIE": 7201326,
        "MOKOTOW": 8722733,
        "WAWER": 3042814,
        "SRODMIESCIE": 4665648,
        "OCHOTA": 3347095,
        "REMBERTOW": 1014271,
        "WLOCHY": 1724261,
        "PRAGA-POLNOC": 2637105,
        "WOLA": 5679919,
        "ZOLIBORZ": 2028543,
        "WESOLA": 1014271,
        "WILANOW": 1521407,
    },
}


# sum check

year = 2025

suma = 0
year_budget = budgets[year]
for budget in year_budget.values():
    suma += budget

print(suma)
