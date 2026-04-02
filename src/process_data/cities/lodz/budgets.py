# https://uml.lodz.pl/budzet-obywatelski/lbo-20232024/podzial-srodkow-w-ramach-lbo/


budgets = {
    2025: {
        "BAŁUTY": {
            "BAŁUTY-CENTRUM": 1228000,
            "BAŁUTY-DOŁY": 1156000,
            "BAŁUTY ZACHODNIE": 551000,
            "JULIANÓW-MARYSIN-ROGI": 642000,
            "ŁAGIEWNIKI": 434000,
            "RADOGOSZCZ": 1010000,
            "TEOFILÓW-WIELKOPOLSKA": 1191000,
            "WZNIESIEŃ ŁÓDZKICH": 429000,
        },
        "GÓRNA": {
            "CHOJNY": 1046000,
            "CHOJNY-DĄBROWA": 1270000,
            "GÓRNIAK": 727000,
            "NAD NEREM": 423000,
            "PIASTÓW-KURAK": 756000,
            "ROKICIE": 724000,
            "RUDA": 624000,
            "WISKITNO": 483000,
        },
        "POLESIE": {
            "KAROLEW-RETKINIA WSCHÓD": 1079000,
            "KOZINY": 582000,
            "LUBLINEK-PIENISTA": 531000,
            "IM. JÓZEFA MONTWIŁŁA-MIRECKIEGO": 431000,
            "RETKINIA ZACHÓD-SMULSKO": 901000,
            "STARE POLESIE": 1006000,
            "ZŁOTNO": 627000,
            "ZDROWIE-MANIA": 473000,
        },
        "ŚRÓDMIEŚCIE": {
            "KATEDRALNA": 1049000,
            "ŚRÓDMIEŚCIE-WSCHÓD": 717000,
        },
        "WIDZEW": {
            "ANDRZEJÓW": 528000,
            "DOLINA ŁÓDKI": 458000,
            "MILESZKI": 453000,
            "NOWOSOLNA": 506000,
            "OLECHÓW-JANÓW": 836000,
            "NR 33": 433000,
            "STARY WIDZEW": 802000,
            "STOKI-SIKAWA-PODGÓRZE": 633000,
            "WIDZEW-WSCHÓD": 1127000,
            "ZARZEW": 784000,
        },
        "CITYWIDE": {"CITYWIDE": 8694120},
    },
    2024: {
        "BAŁUTY": {
            "BAŁUTY-CENTRUM": 1169000,
            "BAŁUTY-DOŁY": 1102000,
            "BAŁUTY ZACHODNIE": 538000,
            "JULIANÓW-MARYSIN-ROGI": 620000,
            "ŁAGIEWNIKI": 430000,
            "RADOGOSZCZ": 960000,
            "TEOFILÓW-WIELKOPOLSKA": 1137000,
            "WZNIESIEŃ ŁÓDZKICH": 426000,
        },
        "GÓRNA": {
            "CHOJNY": 994000,
            "CHOJNY-DĄBROWA": 1211000,
            "GÓRNIAK": 705000,
            "NAD NEREM": 421000,
            "PIASTÓW-KURAK": 733000,
            "ROKICIE": 699000,
            "RUDA": 605000,
            "WISKITNO": 474000,
        },
        "POLESIE": {
            "KAROLEW-RETKINIA WSCHÓD": 1032000,
            "KOZINY": 569000,
            "LUBLINEK-PIENISTA": 515000,
            "IM. JÓZEFA MONTWIŁŁA-MIRECKIEGO": 429000,
            "RETKINIA ZACHÓD-SMULSKO": 862000,
            "STARE POLESIE": 963000,
            "ZŁOTNO": 600000,
            "ZDROWIE-MANIA": 465000,
        },
        "ŚRÓDMIEŚCIE": {
            "KATEDRALNA": 1002000,
            "ŚRÓDMIEŚCIE-WSCHÓD": 693000,
        },
        "WIDZEW": {
            "ANDRZEJÓW": 516000,
            "DOLINA ŁÓDKI": 451000,
            "MILESZKI": 445000,
            "NOWOSOLNA": 493000,
            "OLECHÓW-JANÓW": 799000,
            "NR 33": 429000,
            "STARY WIDZEW": 772000,
            "STOKI-SIKAWA-PODGÓRZE": 612000,
            "WIDZEW-WSCHÓD": 1073000,
            "ZARZEW": 756000,
        },
        "CITYWIDE": {"CITYWIDE": 9632750},
    },
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
