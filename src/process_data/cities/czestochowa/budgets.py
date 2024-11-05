budgets = {
    2025: {
        # https://czestochowa.budzet-obywatelski.eu/wszystko-o-budzecie/podzial-srodkow,59
        "CITYWIDE": 2367122,
        "BLESZNO": 346165,
        "CZESTOCHOWKA-PARKITKA": 326309,
        "DZBOW": 397036,
        "GNASZYN-KAWODRZA": 253512,
        "GRABOWKA": 256582,
        "KIEDRZYN": 204307,
        "LISINIEC": 382831,
        "MIROW": 285194,
        "OSTATNI_GROSZ": 226623,
        "PODJASNOGORSKA": 145947,
        "POLNOC": 686515,
        "RAKOW": 479213,
        "STARE_MIASTO": 263154,
        "STRADOM": 452222,
        "SRODMIESCIE": 339749,
        "TRZECH_WIESZCZOW": 253282,
        "TYSIACLECIE": 656405,
        "WRZOSOWIAK": 566788,
        "WYCZERPY-ANIOLOW": 443816,
        "ZAWODZIE-DABIE": 450661,
    },
    2024: {
        # https://cdnbo.com.pl/gminy/czestochowa/download/10/za%C5%82%C4%85cznik%20nr%201.pdf?WGQ3
        "CITYWIDE": 2367122,
        "BLESZNO": 329457,
        "CZESTOCHOWKA-PARKITKA": 303543,
        "DZBOW": 379410,
        "GNASZYN-KAWODRZA": 241732,
        "GRABOWKA": 250115,
        "KIEDRZYN": 194431,
        "LISINIEC": 364210,
        "MIROW": 272579,
        "OSTATNI_GROSZ": 219426,
        "PODJASNOGORSKA": 138644,
        "POLNOC": 657409,
        "RAKOW": 458964,
        "STARE_MIASTO": 254631,
        "STRADOM": 433989,
        "SRODMIESCIE": 328744,
        "TRZECH_WIESZCZOW": 244728,
        "TYSIACLECIE": 631874,
        "WRZOSOWIAK": 542052,
        "WYCZERPY-ANIOLOW": 422866,
        "ZAWODZIE-DABIE": 432562,
    },
}


# sum check

suma = 0
year = 2024

for budget in budgets[year].values():
    # print(budget)
    suma += budget

print(suma)

# print(suma)