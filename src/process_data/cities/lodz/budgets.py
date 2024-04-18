# https://uml.lodz.pl/budzet-obywatelski/lbo-20232024/podzial-srodkow-w-ramach-lbo/


budgets = {
    2023: {
        "BAŁUTY": {
            "BAŁUTY-CENTRUM": 993000,
            "BAŁUTY-DOŁY": 941000,
            "BAŁUTY ZACHODNIE": 499000,
            "JULIANÓW-MARYSIN-ROGI": 561000,
            "ŁAGIEWNIKI": 422000,
            "RADOGOSZCZ": 819000,
            "TEOFILÓW-WIELKOPOLSKA": 963000,
            "WZNIESIEŃ ŁÓDZKICH": 419000,
        },
        "GÓRNA": {
            "CHOJNY-DĄBROWA": 1002000,
            "CHOJNY": 838000,
            "GÓRNIAK": 627000,
            "NAD NEREM": 415000,
            "PIASTÓW-KURAK": 648000,
            "ROKICIE": 621000,
            "RUDA": 550000,
            "WISKITNO": 453000,
        },
        "POLESIE": {
            "KOZINY": 526000,
            "KAROLEW-RETKINIA WSCHÓD": 868000,
            "LUBLINEK-PIENISTA": 482000,
            "IM. JÓZEFA MONTWIŁŁA-MIRECKIEGO": 421000,
            "RETKINIA ZACHÓD-SMULSKO": 742000,
            "STARE POLESIE": 817000,
            "ZŁOTNO": 539000,
            "ZDROWIE-MANIA": 446000,
        },
        "ŚRÓDMIEŚCIE": {
            "ŚRÓDMIEŚCIE-WSCHÓD": 620000,
            "KATEDRALNA": 851000,
        },
        "WIDZEW": {
            "ANDRZEJÓW": 484000,
            "DOLINA ŁÓDKI": 435000,
            "MILESZKI": 432000,
            "NOWOSOLNA": 465000,
            "NR 33": 420000,
            "OLECHÓW-JANÓW": 691000,
            "STOKI-SIKAWA-PODGÓRZE": 554000,
            "STARY WIDZEW": 675000,
            "WIDZEW-WSCHÓD": 897000,
            "ZARZEW": 664000,
        },
        "CITYWIDE": {"CITYWIDE": 7600000},
    },
}


# sum check

# sum = 0

# for district, budgets in budgets[2023].items():
#     for subdistricts, budget in budgets.items():
#         sum += budget

# sum = "{:,}".format(sum).replace(",", " ")
# print(sum)
