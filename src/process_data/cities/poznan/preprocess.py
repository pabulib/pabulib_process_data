from __future__ import annotations

import csv
import re
from dataclasses import dataclass

import pandas as pd
import requests
from bs4 import BeautifulSoup

import helpers.utilities as utils
from process_data.base_config import BaseConfig
from process_data.cities.poznan.budgets import budgets

VOTING_URL = "https://pbo26.um.poznan.pl/i/pbo/voting"


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.source_votes_csv = self.preprocess["source_votes_csv"]
        self.projects_filename = self.preprocess["projects_filename"]
        self.votes_filename = self.preprocess["votes_filename"]
        return super().__post_init__()

    def parse_int(self, text: str) -> int:
        return int(re.sub(r"[^0-9]", "", text))

    def parse_projects_from_voting_page(self) -> pd.DataFrame:
        self.logger.info("Preprocessing: fetch projects from voting page...")
        html = requests.get(VOTING_URL, timeout=60).text
        soup = BeautifulSoup(html, "html.parser")

        rows = []
        for section in soup.select("section.voting"):
            h3 = section.find_previous("h3")
            if not h3:
                continue
            h3_text = h3.get_text(" ", strip=True)

            if h3_text.startswith(
                "Projekt ogolnomiejski duzy w ramach Zielonego Budzetu"
            ) or h3_text.startswith(
                "Projekt ogólnomiejski duży w ramach Zielonego Budżetu"
            ):
                district = "Zielony Budżet"
                subdistrict = "Zielony Budżet"
            elif h3_text.startswith("Projekt ogolnomiejski duzy") or h3_text.startswith(
                "Projekt ogólnomiejski duży"
            ):
                district = "Ogólnomiejski"
                subdistrict = "duży"
            elif h3_text.startswith("Projekt ogolnomiejski maly") or h3_text.startswith(
                "Projekt ogólnomiejski mały"
            ):
                district = "Ogólnomiejski"
                subdistrict = "mały"
            elif h3_text.startswith("Projekt rejonowy duzy") or h3_text.startswith(
                "Projekt rejonowy duży"
            ):
                h4 = section.find_previous("h4")
                district = h4.get_text(" ", strip=True) if h4 else ""
                subdistrict = "duży"
            elif h3_text.startswith("Projekt rejonowy maly") or h3_text.startswith(
                "Projekt rejonowy mały"
            ):
                h4 = section.find_previous("h4")
                district = h4.get_text(" ", strip=True) if h4 else ""
                subdistrict = "mały"
            else:
                continue

            for row in section.select("div.voting-row"):
                cols = row.find_all("div", recursive=False)
                if len(cols) < 4:
                    continue
                project_id = cols[0].get_text(" ", strip=True).replace("‐", "-")
                title_el = row.select_one("div.voting-col-title a")
                if not title_el:
                    continue
                name = title_el.get_text(" ", strip=True)
                cost = self.parse_int(cols[2].get_text(" ", strip=True))
                votes = self.parse_int(cols[3].get_text(" ", strip=True))
                selected = 1 if "#d0ffd4" in (row.get("style") or "").lower() else 0

                rows.append(
                    {
                        "Numer": project_id,
                        "Nazwa i opis": name,
                        "Koszt": cost,
                        "Liczba głosów": votes,
                        "dzielnica": district,
                        "rodzaj": subdistrict,
                        "czy wybrany": selected,
                    }
                )

        df = pd.DataFrame(rows)
        if df.empty:
            raise RuntimeError("No projects parsed from voting page")

        df = df.drop_duplicates(subset=["Numer"], keep="first")
        df = df.sort_values(by="Numer", key=lambda s: s.astype(str), kind="stable")
        return df

    def parse_votes_csv(self) -> pd.DataFrame:
        self.logger.info("Preprocessing: normalize votes from raw CSV...")
        csv_path = utils.get_path_to_file_by_unit(
            self.source_votes_csv[:-4],
            self.unit,
            extra_dir=self.data_dir,
            ext="csv",
        )

        rows = []
        with open(csv_path, "r", encoding="utf-8", newline="") as file_:
            reader = csv.reader(file_, delimiter=";")
            for line in reader:
                if not line:
                    continue
                voter_raw = line[0].strip()
                if not voter_raw:
                    continue

                voter_id = int(float(voter_raw))
                project_ids = []
                # Source layout: voter_id;project_id;category;project_id;category;...
                for idx in range(1, len(line), 2):
                    token = line[idx].strip()
                    if token and "." in token:
                        project_ids.append(token.replace("‐", "-"))

                # Keep at most one project per category prefix: OD, OM, ZB, RD, RM.
                # This enforces explicit large/small split in citywide and district votes.
                deduped_by_prefix = {}
                for project_id in project_ids:
                    prefix = project_id.split(".")[0]
                    if prefix not in deduped_by_prefix:
                        deduped_by_prefix[prefix] = project_id

                votes = list(deduped_by_prefix.values())
                if not votes:
                    continue

                rows.append({"voter_id": voter_id, "vote": ",".join(votes)})

        df = pd.DataFrame(rows)
        if df.empty:
            raise RuntimeError("No votes parsed from source CSV")
        return df

    def _normalize_budget_keys(self, district: str, subdistrict: str):
        if district == "Ogólnomiejski":
            budget_district = "_CITYWIDE"
        else:
            budget_district = district

        if subdistrict == "duży":
            budget_subdistrict = "large"
        elif subdistrict == "mały":
            budget_subdistrict = "small"
        else:
            budget_subdistrict = subdistrict

        return budget_district, budget_subdistrict

    def apply_poznan_selection_rules(self, projects_df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info(
            "Preprocessing: apply Poznań selection rules (selected=2/3)..."
        )
        df = projects_df.copy()
        df["czy wybrany"] = df["czy wybrany"].astype(int)

        for (district, subdistrict), idxs in df.groupby(
            ["dzielnica", "rodzaj"]
        ).groups.items():
            budget_district, budget_subdistrict = self._normalize_budget_keys(
                district, subdistrict
            )

            try:
                budget = budgets[int(self.instance)][budget_district][
                    budget_subdistrict
                ]
            except KeyError:
                continue

            group_df = df.loc[list(idxs)].sort_values(
                ["Liczba głosów", "Numer"], ascending=[False, True], kind="stable"
            )

            remaining = float(budget)
            regular_project_ids = []
            reserve_project_id = None
            for _, row in group_df.iterrows():
                project_id = row["Numer"]
                cost = float(row["Koszt"])
                if cost <= remaining:
                    regular_project_ids.append(project_id)
                    remaining -= cost
                    continue
                if remaining >= 0.8 * cost:
                    reserve_project_id = project_id
                break

            official_selected_ids = set(
                group_df.loc[group_df["czy wybrany"] == 1, "Numer"].tolist()
            )
            if not official_selected_ids:
                continue

            regular_selected_ids = official_selected_ids.intersection(regular_project_ids)
            external_funds_ids = official_selected_ids.difference(regular_selected_ids)

            reserve_selected_ids = set()
            if reserve_project_id and reserve_project_id in external_funds_ids:
                reserve_selected_ids.add(reserve_project_id)
                external_funds_ids.remove(reserve_project_id)

            group_mask = (df["dzielnica"] == district) & (df["rodzaj"] == subdistrict)
            df.loc[group_mask & (df["Numer"].isin(list(official_selected_ids))), "czy wybrany"] = 1

            if reserve_selected_ids:
                df.loc[
                    group_mask & (df["Numer"].isin(list(reserve_selected_ids))),
                    "czy wybrany",
                ] = 2

            if external_funds_ids:
                df.loc[
                    group_mask & (df["Numer"].isin(list(external_funds_ids))),
                    "czy wybrany",
                ] = 3

        return df

    def save_outputs(self, projects_df: pd.DataFrame, votes_df: pd.DataFrame) -> None:
        projects_xlsx = utils.get_path_to_file_by_unit(
            self.projects_filename, self.unit, extra_dir=self.data_dir, ext="xlsx"
        )
        projects_csv = utils.get_path_to_file_by_unit(
            self.projects_filename, self.unit, extra_dir=self.data_dir, ext="csv"
        )
        votes_xlsx = utils.get_path_to_file_by_unit(
            self.votes_filename, self.unit, extra_dir=self.data_dir, ext="xlsx"
        )
        votes_csv = utils.get_path_to_file_by_unit(
            self.votes_filename, self.unit, extra_dir=self.data_dir, ext="csv"
        )

        projects_df.to_excel(projects_xlsx, index=False)
        projects_df.to_csv(projects_csv, index=False, encoding="utf-8")
        votes_df.to_excel(votes_xlsx, index=False)
        votes_df.to_csv(votes_csv, index=False, encoding="utf-8")

        self.logger.info(f"Saved: {projects_xlsx}")
        self.logger.info(f"Saved: {projects_csv}")
        self.logger.info(f"Saved: {votes_xlsx}")
        self.logger.info(f"Saved: {votes_csv}")

    def start(self):
        self.logger.info("Running preprocessing...")
        projects_df = self.parse_projects_from_voting_page()
        projects_df = self.apply_poznan_selection_rules(projects_df)
        votes_df = self.parse_votes_csv()
        self.save_outputs(projects_df, votes_df)
