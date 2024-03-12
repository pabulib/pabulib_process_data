voting_method_mapping = {"elektronicznie": "internet", "papierowo": "paper"}

selected_mapping = {
    "Wybrany w głosowaniu": 1,
    "Niewybrany w głosowaniu": 0,
    # "Oceniony negatywnie": 0,
}

category_mapping = {
    "edukacja": "education",
    "komunikacja publiczna i drogi": "public transit and roads",
    "komunikacja/drogi": "public transit and roads",
    "kultura": "culture",
    "ochrona środowiska": "environmental protection",
    "zieleń i ochrona środowiska": "environmental protection",
    "pomoc społeczna": "welfare",
    "przestrzeń publiczna": "public space",
    "sport": "sport",
    "sport i infrastruktura sportowa": "sport",
    "zdrowie": "health",
    "zieleń miejska": "urban greenery",
    "bezpieczeństwo": "security",
    "infrastruktura": "infrastructure",
    "społeczeństwo": "society",
    "infrastruktura rowerowa": "bicycle infrastructure",
    "tereny zielone i ochrona środowiska": "environmental protection",
    "infrastruktura komunalna i bezpieczeństwo": "municipal infrastructure and security",
    "infrastruktura drogowa i komunikacja": "public transit and roads",
    "sport i rekreacja": "sport and recreation",
    "kultura i dziedzictwo": "culture",
    "zdrowie i pomoc społeczna": "health and welfare",
    "inne": None,
    "edukacja, dzieci i młodzież": "education, children and youth",
}

target_mapping = {
    "dorosli": "adults",
    "dzieci": "children",
    "mlodziez": "youth",
    "osoby z niepelnosprawnoscia": "people with disabilities",
    "rodziny z dziecmi": "families with children",
    "seniorzy": "seniors",
    "studenci": "students",
    "zwierzeta": "animals",
}

wroclaw_mapping = {
    "drogowe": "roads",
    "nieinwestycyjne": "non-investment",
    "inne": "other",
    "podwórka": "garden squares",
    "zieleń/rekreacja": "greenery/recreation",
    "place zabaw": "playgrounds",
    "inwestycyjny": "investment",
    "piesze/rowerowe": "walking/cycling infrastructure",
    "rewitalizacja": "redevelopment",
    "sport": "sport",
    "komunikacja zbiorowa": "public transit",
    "edukacja": "education",
}
