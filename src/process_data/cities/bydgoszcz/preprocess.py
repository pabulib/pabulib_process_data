import difflib
import os
import re
import unicodedata
from dataclasses import dataclass

import pandas as pd
import pdfplumber

import helpers.settings as helper_settings
from process_data.base_config import BaseConfig


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_votes_excel = self.preprocess["source_votes_excel"]
        self.protocol_pdf = self.preprocess["protocol_pdf"]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        self.space_re = re.compile(r"\s+")
        self.header_re = re.compile(
            r"^(.*?)\s+[–-]\s+Suma środków przeznaczonych na zadania"
            r"(?: osiedlowe)? w 2025 roku:\s*([\d\s]+)\s*zł",
            re.I,
        )
        self.micro_re = re.compile(
            r"^(.*?)\s+[–-]\s+mikroprojekty osiedlowe:\s*([\d\s]+)\s*zł",
            re.I,
        )
        return super().__post_init__()

    def get_source_path(self, filename, ext):
        return os.path.join(
            helper_settings.get_path_to_excel_files(self.unit, self.data_dir),
            f"{filename}.{ext}",
        ).replace("\\", "/")

    def get_output_path(self, filename):
        output_dir = helper_settings.get_path_to_excel_files(self.unit, self.data_dir)
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{filename}.xlsx").replace("\\", "/")

    def clean_text(self, text):
        text = str(text or "").replace("\n", " ").replace("\xa0", " ")
        return self.space_re.sub(" ", text).strip()

    def normalize_key(self, text):
        text = self.clean_text(text)
        text = text.replace("–", "-").replace("—", "-")
        text = text.replace("Śródmieście - Miasto", "Śródmieście - Stare Miasto")
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()

    def parse_int(self, text):
        return int(re.sub(r"\D", "", str(text or "0")) or 0)

    def parse_section(self, text):
        text = self.clean_text(text)
        if not text:
            return None

        header_match = self.header_re.match(text)
        if header_match:
            name = self.clean_text(header_match.group(1))
            budget = self.parse_int(header_match.group(2))
            if name.upper().startswith("PROJEKTY PONAD"):
                return "Ponadosiedlowy", "Ponadosiedlowe", budget
            if name.lower().startswith("projekty społ"):
                return "Społeczny", "Społeczne", budget
            return "Osiedlowy", self.canonical_pool_name(name), budget

        micro_match = self.micro_re.match(text)
        if micro_match:
            name = self.canonical_pool_name(self.clean_text(micro_match.group(1)))
            budget = self.parse_int(micro_match.group(2))
            return "Mikroprojekt osiedlowy", f"{name} - mikroprojekty", budget

        return None

    def canonical_pool_name(self, name):
        replacements = {
            "Bocianowo – Śródmieście - Miasto": (
                "Bocianowo - Śródmieście - Stare Miasto"
            ),
            "Bocianowo - Śródmieście - Miasto": (
                "Bocianowo - Śródmieście - Stare Miasto"
            ),
            "Miedzyń – Prądy": "Miedzyń - Prądy",
            "Smukała-Opławiec-Janowo": "Smukała - Opławiec - Janowo",
            "Wilczak-Jary": "Wilczak - Jary",
            "Zimne Wody – Czersko Polskie": "Zimne Wody - Czersko Polskie",
        }
        name = self.clean_text(name).title()
        return replacements.get(name, name)

    def parse_protocol_projects(self):
        projects = []
        current_section = None
        pdf_path = self.get_source_path(self.protocol_pdf, "pdf")

        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages[5:], start=6):
                for table in page.extract_tables() or []:
                    for row in table:
                        if not row:
                            continue
                        first_cell = self.clean_text(row[0]) if row else ""
                        parsed_section = self.parse_section(first_cell)
                        if parsed_section:
                            current_section = parsed_section
                            continue
                        if (
                            not first_cell
                            or first_cell == "Nr"
                            or first_cell == "Razem"
                            or "Suma środków" in first_cell
                            or "mikroprojekty osiedlowe" in first_cell
                        ):
                            continue
                        if not re.fullmatch(r"\d+", first_cell):
                            continue
                        if current_section is None:
                            raise RuntimeError(
                                f"Bydgoszcz protocol row without section: {row}"
                            )
                        if len(row) < 6:
                            raise RuntimeError(
                                f"Bydgoszcz protocol row too short on page "
                                f"{page_number}: {row}"
                            )

                        category, district, budget = current_section
                        projects.append(
                            {
                                "project_id": first_cell,
                                "category": category,
                                "district": district,
                                "name": self.clean_text(row[1]),
                                "cost": self.parse_int(row[3]),
                                "protocol_votes": self.parse_int(row[4]),
                                "selected": self.parse_selected(row[5]),
                                "budget": budget,
                                "source": f"protocol page {page_number}",
                            }
                        )

        projects.extend(self.manual_protocol_rows())
        return pd.DataFrame(projects)

    def manual_protocol_rows(self):
        rows = [
            ("Ponadosiedlowy", "Ponadosiedlowe", "193", "Rzeźba KOGUTA Mistrza Twardowskiego", 200000, 593, 0, 1540000),
            ("Społeczny", "Społeczne", "19", "Fordońskie Kino pod Chmurką", 38600, 496, 1, 38600),
            ("Społeczny", "Społeczne", "372", "Wróżka Nelly – Listy Nadziei dla Dzieci Onkologicznych", 25000, 311, 1, 38600),
            ("Społeczny", "Społeczne", "223", "Aromatyczny kącik, ze strefą wypoczynkową.", 38600, 184, 0, 38600),
            ("Społeczny", "Społeczne", "110", '"Zakręcone Okole – rowerowy rajd mieszkańców"', 36600, 48, 0, 38600),
            ("Mikroprojekt osiedlowy", "Miedzyń - Prądy - mikroprojekty", "490", "Rowerowa wycieczka turystyczna", 9797, 49, 0, 10000),
            ("Osiedlowy", "Bartodzieje", "79", "Utwardzenie kostką Polbruk ulicy Redłowskiej na długości 150 m.", 404561, 26, 0, 809122),
            ("Osiedlowy", "Bocianowo - Śródmieście - Stare Miasto", "514", "Kogut Twardowskiego – bajkowa rzeźba dla Bydgoszczy", 165000, 56, 0, 832927),
            ("Osiedlowy", "Bocianowo - Śródmieście - Stare Miasto", "415", "postawienie ławek wraz z koszami na odpadki na ul. Tamki /odcinek alei kasztanowej/", 50000, 7, 0, 832927),
            ("Osiedlowy", "Czyżkówko", "292", "częściowe utwardzenie ulicy Odonica", 281498, 33, 0, 562997),
            ("Osiedlowy", "Kapuściska", "196", "Kontynuacja wymiany nawierzchni z asfaltowej na mineralną, wodoprzepuszczalną przy Noakowskiego", 360593, 61, 0, 721187),
            ("Osiedlowy", "Nowy Fordon", "363", "Osiedlowy Park Eskulapa", 457012, 79, 0, 970025),
            ("Osiedlowy", "Osowa Góra", "210", "Budowa i modernizacja wiat przystankowych przy ulicach Kruszyńskiej, Podmiejskiej i Srebrnej", 160000, 21, 0, 507683),
            ("Osiedlowy", "Wyżyny", "440", "Wybieg dla psów - ul. Staffa", 462158, 61, 0, 924315),
        ]
        return [
            {
                "category": category,
                "district": district,
                "project_id": project_id,
                "name": name,
                "cost": cost,
                "protocol_votes": protocol_votes,
                "selected": selected,
                "budget": budget,
                "source": "manual protocol text fallback",
            }
            for (
                category,
                district,
                project_id,
                name,
                cost,
                protocol_votes,
                selected,
                budget,
            ) in rows
        ]

    def parse_selected(self, text):
        return 1 if self.clean_text(text).upper() == "TAK" else 0

    def load_votes_source(self):
        path = self.get_source_path(self.source_votes_excel, "xlsx")
        votes_df = pd.read_excel(path)
        expected = {
            "ID głosu",
            "Płeć",
            "Wiek",
            "Projekt",
            "Osiedle projektu",
            "Kategoria",
            "Status akceptacji",
            "Rok BBO",
            "Typ głosowania",
        }
        missing = expected.difference(votes_df.columns)
        if missing:
            raise RuntimeError(f"Missing Bydgoszcz votes columns: {sorted(missing)}")
        return votes_df

    def build_vote_groups(self, votes_df):
        accepted = votes_df[votes_df["Status akceptacji"] == "Zaakceptowany"].copy()
        accepted["district"] = accepted["Osiedle projektu"]
        citywide = accepted["Kategoria"].isin(["Ponadosiedlowy", "Społeczny"])
        accepted.loc[citywide, "district"] = accepted.loc[citywide, "Kategoria"]
        accepted["district"] = accepted.apply(
            lambda row: self.pool_name(row["Kategoria"], row["district"]), axis=1
        )
        grouped = (
            accepted.groupby(["Kategoria", "district", "Projekt"], dropna=False)
            .size()
            .reset_index(name="votes")
        )
        return accepted, grouped

    def pool_name(self, category, district):
        if category == "Ponadosiedlowy":
            return "Ponadosiedlowe"
        if category == "Społeczny":
            return "Społeczne"
        district = self.canonical_pool_name(district)
        if category == "Mikroprojekt osiedlowy":
            return f"{district} - mikroprojekty"
        return district

    def similarity(self, left, right):
        return difflib.SequenceMatcher(
            None, self.normalize_key(left), self.normalize_key(right)
        ).ratio()

    def match_projects(self, protocol_df, vote_groups):
        protocol_df = protocol_df.copy()
        protocol_df["district_key"] = protocol_df["district"].map(self.normalize_key)
        matched = []
        used_indexes = set()

        for _, group in vote_groups.iterrows():
            category = group["Kategoria"]
            district = group["district"]
            votes = int(group["votes"])
            candidates = protocol_df[
                (protocol_df["category"] == category)
                & (protocol_df["district_key"] == self.normalize_key(district))
                & (protocol_df["protocol_votes"] == votes)
            ]

            if candidates.empty:
                candidates = protocol_df[
                    (protocol_df["category"] == category)
                    & (protocol_df["district_key"] == self.normalize_key(district))
                ]
                candidates = candidates.assign(
                    similarity=candidates["name"].map(
                        lambda name: self.similarity(group["Projekt"], name)
                    )
                ).sort_values("similarity", ascending=False)
                if candidates.empty or candidates.iloc[0]["similarity"] < 0.8:
                    raise RuntimeError(
                        "Cannot match Bydgoszcz project: "
                        f"{category} | {district} | {group['Projekt']} | {votes}"
                    )
                candidates = candidates.head(1)
            elif len(candidates) > 1:
                candidates = candidates.assign(
                    similarity=candidates["name"].map(
                        lambda name: self.similarity(group["Projekt"], name)
                    )
                ).sort_values("similarity", ascending=False)
                top = candidates.iloc[0]
                if top["similarity"] < 0.45:
                    raise RuntimeError(
                        "Ambiguous Bydgoszcz project match: "
                        f"{category} | {district} | {group['Projekt']} | {votes}"
                    )
                candidates = candidates.head(1)

            project = candidates.iloc[0]
            used_indexes.add(project.name)
            matched.append(
                {
                    "project_id": str(project["project_id"]),
                    "name": self.clean_text(group["Projekt"]),
                    "cost": int(project["cost"]),
                    "votes": votes,
                    "protocol_votes": int(project["protocol_votes"]),
                    "district": district,
                    "selected": int(project["selected"]),
                    "category": category,
                }
            )

        unused = protocol_df.drop(index=list(used_indexes))
        if not unused.empty:
            raise RuntimeError(
                "Unmatched Bydgoszcz protocol projects: "
                f"{unused[['category', 'district', 'project_id', 'name']].to_dict('records')}"
            )

        return pd.DataFrame(matched)

    def build_votes_output(self, accepted_votes, projects_df):
        lookup = {
            (
                row["category"],
                self.normalize_key(row["district"]),
                self.normalize_key(row["name"]),
            ): row["project_id"]
            for _, row in projects_df.iterrows()
        }

        rows = []
        for _, row in accepted_votes.iterrows():
            district = self.pool_name(row["Kategoria"], row["Osiedle projektu"])
            key = (
                row["Kategoria"],
                self.normalize_key(district),
                self.normalize_key(row["Projekt"]),
            )
            project_id = lookup.get(key)
            if project_id is None:
                raise RuntimeError(f"Cannot map Bydgoszcz vote row: {row.to_dict()}")
            rows.append(
                {
                    "voter_id": row["ID głosu"],
                    "age": int(row["Wiek"]),
                    "sex": row["Płeć"],
                    "voting_method": "internet",
                    "district": district,
                    "vote": project_id,
                }
            )
        return pd.DataFrame(rows)

    def validate(self, votes_df, accepted_votes, projects_df, votes_output):
        if len(votes_df) != 56825:
            raise RuntimeError(f"Expected 56,825 Bydgoszcz rows, got {len(votes_df)}")
        if len(accepted_votes) != 56700:
            raise RuntimeError(
                f"Expected 56,700 accepted Bydgoszcz rows, got {len(accepted_votes)}"
            )
        if len(votes_df[votes_df["Status akceptacji"] != "Zaakceptowany"]) != 125:
            raise RuntimeError("Expected 125 rejected Bydgoszcz rows")
        if len(projects_df) != 268:
            raise RuntimeError(
                f"Expected 268 Bydgoszcz project-pool rows, got {len(projects_df)}"
            )
        if len(votes_output) != 56700:
            raise RuntimeError(
                f"Expected 56,700 Bydgoszcz output votes, got {len(votes_output)}"
            )

        mismatches = projects_df[projects_df["votes"] != projects_df["protocol_votes"]]
        expected = {
            ("466", 173, 174),
            ("371", 198, 199),
        }
        actual = {
            (str(row["project_id"]), int(row["votes"]), int(row["protocol_votes"]))
            for _, row in mismatches.iterrows()
        }
        if actual != expected:
            raise RuntimeError(f"Unexpected Bydgoszcz source mismatches: {actual}")

    def start(self):
        self.logger.info("Running Bydgoszcz preprocessing...")
        protocol_projects = self.parse_protocol_projects()
        votes_source = self.load_votes_source()
        accepted_votes, vote_groups = self.build_vote_groups(votes_source)
        projects_output = self.match_projects(protocol_projects, vote_groups)
        votes_output = self.build_votes_output(accepted_votes, projects_output)
        self.validate(votes_source, accepted_votes, projects_output, votes_output)

        projects_output.drop(columns=["protocol_votes", "category"]).to_excel(
            self.get_output_path(self.projects_excel), index=False
        )
        votes_output.to_excel(self.get_output_path(self.votes_excel), index=False)
        self.logger.info("Bydgoszcz preprocessing finished.")
