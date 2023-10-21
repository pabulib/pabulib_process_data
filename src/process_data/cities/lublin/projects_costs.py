import re

pattern = r"([DO] - \d{1,3}) .*?(\d{3,})"

text = """
D - 0 Felin Drogi 150000
O - 1 Tereny zielone 1100000
O - 2 Rury, Wieniawa NOWE CHODNIKI na Dzielnicy Rury (LSM). Drogi 1200000
O - 3 Kalinowszczyzna Tereny zielone 816600
O - 4 Zemborzyce Drogi 1056000
O - 5 Zwierzęta 300000
O - 6 oBiegowa dolina Czechówki Tereny zielone 1200000
O - 7 Animacja społeczna 299000
O - 8 Zielony Lublin Tereny zielone 291000
O - 9 Obiekty sportowe 1200000
O - 10 Razem dbamy o zwierzęta w mieście Zwierzęta 290000
O - 11 Cisza na Czubach Drogi 200000
O - 12 Tramwaje w Lublinie Transport 900000
O - 13 Kultura się liczy! - Domy Kultury Przestrzeni Kultura 300000
O - 14 Obiekty sportowe 1200000
O - 15 Drogi 1200000
O - 16 Stop mordowaniu dzieci Drogi 1200000
O - 17 inne 60000 Projekt zakłada przeprowadzenie badania społecznego na temat powodów absencji w referendum 7 kwietnia w Lublinie.
O - 18 Stare Miasto Klub Mahjong Kultura 1200000 Pierwszy klub do gry w mahjonga.
O - 19 Tatary Place zabaw 1200000
O - 20 Bezpieczne przejścia dla pieszych Drogi 1099050
O - 21 Śródmieście Lublin Przyjazny Rowerzystom Drogi 1200000
O - 22 Rury Drogi 1200000
O - 23 Tereny zielone 342900
O - 24 inne 250000
O - 25 Rozwijamy Lubelski FUTSAL! inne 165000
O - 26 Rury Drogi 1200000
O - 27 Aktywny uczeń Dzieciaki 300000
O - 28 Drogi 1200000
O - 29 Zajęcia sportowe 53680
O - 30 Mieszkania dla Lublinian inne 1200000
O - 31 Dzieciaki 1200000 Projekt obejmuje kompleksowy remont pomieszczeń kuchni szkolnej z wraz z ich wyposażeniem.
O - 32 Bronowice, Felin Remont ulicy Jaskółczej Drogi 1129800
O - 33 inne 1200000
O - 34 Obiekty sportowe 406000
O - 35 Aktywizacja sportowa dzieci Zajęcia sportowe 150500
O - 36 Obiekty sportowe 1200000
O - 37 Zemborzyce Tereny zielone 1200000
O - 38 Kalinowszczyzna INWESTYCJE NA KALINIE Tereny zielone 1200000
O - 39 inne 300000
O - 40 Edukacyjny wypas owiec. Animacja społeczna 30250
O - 41 Tereny zielone 1200000
O - 42 Aktywni Młodzi Zajęcia sportowe 300000
O - 43 MIASTO PIĘKNA I SZTUKI Kultura 300000
O - 44 Dzieciaki 125600
O - 45 Amatorskie Ligi Lublina Zajęcia sportowe 300000
O - 46 Sławin, Sławinek Ścieżka rowerowa w Alei Warszawskiej Drogi 1200000
O - 47 przeRysowani Kultura 12160
O - 48 Kultura 240000
O - 49 Obiekty sportowe 1200000
O - 50 inne 1042010
O - 51 Obiekty sportowe 1200000
O - 52 Miasto kamienic inne 1200000
O - 53 Drogi 1200000
O - 54 Tereny zielone 1199999
O - 55 Drogi 1200000
O - 56 Animacja społeczna 45000
O - 57 Lubelska Akademia Koszykówki Zajęcia sportowe 300000
O - 58 Poznaj cudzoziemca swego Kultura 10820
O - 59 Dzieciaki 300000
O - 60 Śródmieście Kultura 300000
O - 61 Animacja społeczna 155920
O - 62 Aktywny Lublin Drogi 300000
O - 63 Pokochaj Bieganie w Lublinie! Zajęcia sportowe 300000
O - 64 inne 250000
O - 65 inne 400000
O - 66 Śródmieście Kultura 1200000
O - 67 Obiekty sportowe 1200000
O - 68 Drogi 1200000
O - 69 Tereny zielone 1200000
O - 70 Tereny zielone 1200000
O - 71 inne 108000
O - 72 Place zabaw 164400
O - 73 Czuby Północne Drogi 1200000
O - 74 Czuby Północne Drogi 1200000
D - 1 Rury NOWE PARKINGI na Dzielnicy Rury (LSM) Parkingi 300000
D - 2 Rury Drogi 300000
D - 3 Węglin Północny Drogi 300000
D - 4 Hajdów-Zadębie Zajęcia Kulturalne Hajdów-Zadębie Kultura 16940
D - 5 Stare Miasto Nowe życie podwórka Jezuicka 14 Tereny zielone 250000
D - 6 Kośminek Drogi 300000
D - 7 Węglin Północny Przyjazny Skwer Na Węglinie Północnym Tereny zielone 299980
D - 8 Felin Ścieżka rowerowa na Felinie Drogi 300000
D - 9 Bronowice Parkingi 300000
D - 10 Głusk Drogi 300000
D - 11 Węglin Północny Drogi 299000
D - 12 Kalinowszczyzna Tereny zielone 184485
D - 13 Tramwaj - kawiarnia w Lublinie Animacja społeczna 115000
D - 14 Za Cukrownią Malowanie rur inne 200000
D - 15 Ponikwoda Dzieciaki 235000
D - 16 Schody na Szczytową Drogi 164210
D - 17 Równa Wyżynna Drogi 136500
D - 18 Wieniawa Parkingi 40000
D - 19 Felin Place zabaw 300000
D - 20 inne 46200
D - 21 Konstantynów Remont ulic Borelowskiego i Kruka Drogi 300000
D - 22 Felin inne 157500
D - 23 Drogi 300000
D - 24 Czuby Północne Drogi 297505
D - 25 Zemborzyce 265000
D - 26 Konstantynów Kolorowe marzenie dzieci Place zabaw 233100
D - 27 Konstantynów inne 300000
D - 28 Bronowice inne 300000
D - 29 Kośminek inne 300000
D - 30 Sławinek inne 300000
D - 31 Ponikwoda inne 300000
D - 32 Abramowice inne 300000
D - 33 Tatary inne 300000
D - 34 Głusk inne 300000
D - 35 Dziesiąta inne 300000
D - 36 Tatary Nowe parkingi na Tatarach Parkingi 300000
D - 37 Bronowice Parkingi 300000
D - 38 Sławin Tereny zielone 286000
D - 39 Szerokie Drogi 300000
D - 40 Felin PLAC ZABAW NA FELINIE Place zabaw 300000
D - 41 Remont obiektów sportowych SP16 Obiekty sportowe 300000
D - 42 Zajęcia sportowe 265000
D - 43 Dziesiąta Tereny zielone 300000
D - 44 Zajęcia sportowe 300000 Rozwój sportu i rekreacji na Czechowie Północnym
D - 45 Rury Obiekty sportowe 131400
D - 46 Rury Dzieciaki 90000
D - 47 Wrotków Kultura 300000
D - 48 Głusk inne 292891
D - 49 Dziesiąta Nowy Świat dla dzieci Drogi 300000
D - 50 Place zabaw 294820
D - 51 Śródmieście Nowe miejsca parkingowe w Śródmieściu Drogi 300000
D - 52 Felin Bezpieczna droga do szkoły na Felinie Drogi 300000
D - 53 Śródmieście Place zabaw 280000
D - 54 Dziesiąta Obiekty sportowe 299900
D - 55 Głusk Utwardzenie placu przy ul.Miodowej Parkingi 255000 Utwardzenie placu przy ul. Miodowej, Dz.116 Obr. 67 Ark. 1
D - 56 inne 300000
D - 57 Węglin Północny Drogi 300000
D - 58 Wrotków inne 300000
D - 59 Za Cukrownią inne 300000
D - 60 Zemborzyce inne 300000
D - 61 Konstantynów Drogi 299000
D - 62 Abramowice Drogi 300000
D - 63 Śródmieście Zieleń przy Niecałej inne 116000 Projekt polega na ustawieniu donic wraz z nasadzeniem w nich berberysów w celu ożywienia/upiększenia ulicy Niecałej.
D - 64 Ponikwoda Wybieg dla psów przy ulicy Węglarza. Zwierzęta 65000
D - 65 Stare Miasto Drogi 300000
D - 66 Kalinowszczyzna Parkingi 300000
D - 67 Ponikwoda Remont chodników Drogi 300000 Remont chodników przy ulicy Owocowej,Jarzębinowej oraz Śliwkowej.
D - 68 Wieniawa Wolna Strefa Studenta inne 231380
D - 69 Place zabaw 300000
D - 70 Sławin Oświetlenie ulica Fiołkowa Drogi 24000
D - 71 Kośminek Obiekty sportowe 300000
D - 72 Tereny zielone 300000
D - 73 Rury Remont skateparku przy ul. Rycerskiej Tereny zielone 300000 Remont skateparku przy ul. Rycerskiej. Zapewnienie bezpieczeństwa użytkowników, zmiany w projekcie.
D - 74 Sławinek inne 300000
D - 75 Bronowice Pogodna ulica sąsiadów zachwyca Drogi 210000
D - 76 Śródmieście Zmniejszamy zadłużenie miasta inne 300000
D - 77 Ponikwoda Tereny zielone 296000
D - 78 Zemborzyce Drogi 168000
D - 79 Obiekty sportowe 299970
D - 80 Aktywny Przedszkolak Zajęcia sportowe 300000
D - 81 Wieniawa Aktywna Wieniawa Zajęcia sportowe 300000
D - 82 Za Cukrownią inne 193880
D - 83 Za Cukrownią Aktywny Lublin Zajęcia sportowe 300000
D - 84 Konstantynów Aktywny Konstantynów Zajęcia sportowe 300000
D - 85 Hajdów-Zadębie Place zabaw 294600
D - 86 Sławinek Nasza Dzielnica - Nasz Sławinek inne 300000
D - 87 Hajdów-Zadębie inne 290000
D - 88 Sławinek Nasz Sławinek Drogi 300000
D - 89 Zemborzyce Drogi 294000
D - 90 Ponikwoda Transport 215000
D - 91 Obiekty sportowe 210000
D - 92 Hajdów-Zadębie Drogi 299500
D - 93 Kośminek Kośminek - Relaks nad rzeką Czerniejówką Place zabaw 150000
D - 94 Sławinek Place zabaw 70000
D - 95 Kośminek Drogi 150000 Zaprojektowanie i wykonanie 3 bezpiecznych przejść przez jednię w okolicy przystanków autobusowych na ulicy Wyzwolenia
D - 96 Hajdów-Zadębie inne 290000
D - 97 Obiekty sportowe 300000
D - 98 Abramowice Abramowicką bezpiecznie rowerem Drogi 300000 Projekt zakłada zaprojektowanie i wykonanie brakującego odcinka drogi rowerowej wzdłuż ul. Abramowickiej.
D - 99 Stare Miasto Szpilkostrada na Starym Mieście Drogi 300000
D - 100 Sławin Drogi 300000
D - 101 Transport 300000
D - 102 Felin Park centralny na Felinie Tereny zielone 300000
D - 103 Wrotków Rowerem i rolkami wygodnie nad Bystrzycę Drogi 300000
D - 104 Rury Place zabaw 263500
D - 105 Śródmieście Obiekty sportowe 300000
D - 106 Budowa siłowni przy ulicy J.Kiepury 100000
D - 107 Zemborzyce Tereny zielone 300000
D - 108 Bronowice Dzieciaki 300000
D - 109 Kośminek inne 300000
D - 110 Dziesiąta Ulica Piękna - remont chodników Drogi 200000
D - 111 Hajdów-Zadębie Łagiewnicką nad rzekę Drogi 300000
D - 112 Dziesiąta Tereny zielone 100000
D - 113 Bronowice REWITALIZACJA STARYCH BRONOWIC Drogi 250000
D - 114 Rury Dzieciaki 261000
D - 115 Bronowice Zajęcia sportowe 300000
D - 116 Sławin inne 300000
D - 117 Rury Dzieciaki 299999.99
D - 118 Czuby Północne Drogi 297505
D - 119 Hajdów-Zadębie inne 300000
D - 120 inne 88735
D - 121 Rury Kultura 165000
D - 122 Rury Place zabaw 183750 Rewitalizacja placu zabaw przy ul. Głębokiej 20,22,24 w Lublinie.
D - 123 Za Cukrownią Odwodnienie ulicy Dzierżawnej Drogi 300000
D - 124 Czuby Północne Drogi 300000
D - 125 Śródmieście Drogi 189000
D - 126 Felin Drogi 150000
D - 127 Oświetlenie 150000
O - 78 Aktywne Pokolenie 68785
O - 79 Aktywny Lublin 300000
O - 76 Czechów - aktywnie i zdrowo - piłka nożna dla najmłodszych 265000
D - 128 Budowa siłowni plenerowej 55000
D - 129 Remont ulicy Jaskółczej 1129800
O - 77 Aktywny Przedszkolak	300000
O - 75 Zajęcia Kulturalne Hajdów-Zadębie 20000
O - 81 L.S.M. - Lubelska Stolica Muzyki, dzielnicowy koncert artystów wywodzących się z OS. "LSM" dla mieszkańców 165000
O - 80 Aktywny Konstantynów	300000
"""


def get_projects_costs():

    projects_costs = dict()

    for project_line in text.split("\n"):
        if project_line:
            try:
                project_id = re.match(pattern, project_line).group(1)
                project_id = project_id.replace(" ", "")
                cost = re.match(pattern, project_line).group(2)
                projects_costs[project_id] = int(cost)
            except AttributeError:
                raise RuntimeError(f"There is no cost in line: {project_line}")

    return projects_costs
