import os
from dataclasses import dataclass

import pandas as pd

import helpers.settings as helper_settings
from process_data.base_config import BaseConfig


CATEGORY_MAPPING = {
    "Esélyteremtő Budapest": "Social",
    "Helyi - kis ötlet": "Local Small Idea",
    "Helyi - nagy ötlet": "Local Big Idea",
    "Nyitott Budapest": "Open",
    "Zöld Budapest": "Green",
}


@dataclass(kw_only=True)
class Preprocess(BaseConfig):
    preprocess: dict

    def __post_init__(self):
        self.data_dir = self.preprocess["data_dir"]
        self.projects_source_excel = self.preprocess["projects_source_excel"]
        self.votes_source_excel = self.preprocess["votes_source_excel"]
        self.complete_selections_source_excel = self.preprocess[
            "complete_selections_source_excel"
        ]
        self.projects_excel = self.preprocess["projects_excel"]
        self.votes_excel = self.preprocess["votes_excel"]
        self.project_vote_totals_source = self.preprocess[
            "project_vote_totals_source"
        ]
        self.expected_unknown_project_rows = self.preprocess[
            "expected_unknown_project_rows"
        ]
        self.expected_unlinked_vote_rows = self.preprocess[
            "expected_unlinked_vote_rows"
        ]
        self.expected_repeated_project_rows = self.preprocess[
            "expected_repeated_project_rows"
        ]
        return super().__post_init__()

    def get_source_path(self, filename):
        return os.path.join(
            helper_settings.get_path_to_excel_files(
                self.unit,
                extra_dir=os.path.join(self.data_dir, "raw"),
            ),
            f"{filename}.xlsx",
        ).replace("\\", "/")

    def get_output_path(self, filename):
        output_dir = helper_settings.get_path_to_excel_files(
            self.unit,
            extra_dir=self.data_dir,
        )
        os.makedirs(output_dir, exist_ok=True)
        return os.path.join(output_dir, f"{filename}.xlsx").replace("\\", "/")

    def load_projects(self):
        df = pd.read_excel(self.get_source_path(self.projects_source_excel))
        missing_categories = sorted(set(df["name"]).difference(CATEGORY_MAPPING))
        if missing_categories:
            raise RuntimeError(f"Unknown Budapest categories: {missing_categories}")

        projects_df = pd.DataFrame(
            {
                "project_id": df["id"].astype(int).astype(str),
                "cost": df["cost"].astype(int),
                "votes": df["online_vote_count"].astype(int),
                "name": df["title.1"].astype(str).str.strip(),
                "category": df["name"].map(CATEGORY_MAPPING),
                "selected": df["win"].astype(int),
                "latitude": df["latitude"],
                "longitude": df["longitude"],
            }
        )
        return projects_df

    def load_votes(self, projects_df):
        raw_votes = pd.read_excel(self.get_source_path(self.votes_source_excel))
        project_ids = set(projects_df["project_id"])
        raw_votes["project_id"] = (
            raw_votes["Projekt azonosító"].astype(int).astype(str)
        )
        votes_df = raw_votes[raw_votes["project_id"].isin(project_ids)].copy()

        grouped = (
            votes_df.sort_values(["Szavazó", "Szavazat leadás időpontja"])
            .groupby("Szavazó")["project_id"]
            .agg(lambda values: ",".join(values))
            .reset_index()
            .rename(columns={"Szavazó": "voter_id", "project_id": "vote"})
        )
        grouped["voting_method"] = "internet"

        return raw_votes, votes_df, grouped

    def load_complete_vote_rows(self, projects_df):
        complete_votes = pd.read_excel(
            self.get_source_path(self.complete_selections_source_excel)
        )
        complete_votes["project_id"] = (
            complete_votes["Projekt azonosító"].astype(int).astype(str)
        )
        project_ids = set(projects_df["project_id"])
        unknown_project_ids = sorted(
            set(complete_votes["project_id"]).difference(project_ids)
        )
        if unknown_project_ids:
            raise RuntimeError(
                "Complete Budapest vote export contains unknown projects: "
                f"{unknown_project_ids}"
            )
        return complete_votes

    def validate(
        self,
        projects_df,
        raw_votes_df,
        vote_rows_df,
        grouped_votes_df,
        complete_vote_rows_df,
    ):
        if self.project_vote_totals_source != "reconstructable_ballots":
            raise RuntimeError(
                "Budapest project_vote_totals_source must be "
                "reconstructable_ballots"
            )

        unknown_project_rows = len(raw_votes_df) - len(vote_rows_df)
        if unknown_project_rows != self.expected_unknown_project_rows:
            raise RuntimeError(
                "Unexpected number of Budapest vote rows for unknown projects: "
                f"expected {self.expected_unknown_project_rows}, got "
                f"{unknown_project_rows}"
            )

        ballot_lengths = grouped_votes_df["vote"].str.split(",").str.len()
        invalid_ballot_lengths = ballot_lengths[
            (ballot_lengths < 1) | (ballot_lengths > 15)
        ]
        if not invalid_ballot_lengths.empty:
            raise RuntimeError(
                "Budapest ballots outside the permitted length range: "
                f"{invalid_ballot_lengths.head(20).to_dict()}"
            )

        category_lengths = vote_rows_df.groupby(["Szavazó", "Kategória"]).size()
        invalid_category_lengths = category_lengths[category_lengths > 3]
        if not invalid_category_lengths.empty:
            raise RuntimeError(
                "Budapest ballots exceed the three-project category limit: "
                f"{invalid_category_lengths.head(20).to_dict()}"
            )

        repeated_project_rows = int(
            vote_rows_df.duplicated(["Szavazó", "project_id"]).sum()
        )
        if repeated_project_rows != self.expected_repeated_project_rows:
            raise RuntimeError(
                "Unexpected number of repeated Budapest project selections: "
                f"expected {self.expected_repeated_project_rows}, got "
                f"{repeated_project_rows}"
            )

        official_counts = projects_df.set_index("project_id")["votes"].astype(int)
        complete_counts = (
            complete_vote_rows_df.groupby("project_id")
            .size()
            .reindex(official_counts.index, fill_value=0)
        )
        if not complete_counts.equals(official_counts):
            differences = official_counts - complete_counts
            raise RuntimeError(
                "Complete Budapest vote export does not match official totals: "
                f"{differences[differences != 0].to_dict()}"
            )

        complete_voter_ids = complete_vote_rows_df["Szavazó"].nunique(dropna=False)
        if complete_voter_ids != 1:
            raise RuntimeError(
                "Expected one technical voter ID in the complete Budapest export, "
                f"got {complete_voter_ids}"
            )

        comparison_columns = [
            "Szavazat leadás időpontja",
            "project_id",
            "Projekt név",
            "Kategória",
        ]
        linked_keys = vote_rows_df.value_counts(
            comparison_columns, dropna=False
        )
        complete_keys = complete_vote_rows_df.value_counts(
            comparison_columns, dropna=False
        )
        all_keys = linked_keys.index.union(complete_keys.index)
        linked_keys = linked_keys.reindex(all_keys, fill_value=0)
        complete_keys = complete_keys.reindex(all_keys, fill_value=0)
        if (linked_keys > complete_keys).any():
            raise RuntimeError(
                "The reconstructable Budapest ballots contain selections absent "
                "from the complete export"
            )
        complete_export_unlinked_rows = int((complete_keys - linked_keys).sum())

        linked_counts = (
            vote_rows_df.groupby("project_id")
            .size()
            .reindex(official_counts.index, fill_value=0)
        )
        differences = official_counts - linked_counts
        if (differences < 0).any():
            raise RuntimeError(
                "Budapest vote-level data exceeds official project totals: "
                f"{differences[differences < 0].to_dict()}"
            )

        unlinked_vote_rows = int(differences.sum())
        if unlinked_vote_rows != self.expected_unlinked_vote_rows:
            raise RuntimeError(
                "Unexpected number of unlinked Budapest vote rows: "
                f"expected {self.expected_unlinked_vote_rows}, got "
                f"{unlinked_vote_rows}; differences="
                f"{differences[differences != 0].to_dict()}"
            )
        if complete_export_unlinked_rows != self.expected_unlinked_vote_rows:
            raise RuntimeError(
                "Unexpected number of selections without reconstructable ballots "
                "in the complete Budapest export: "
                f"expected {self.expected_unlinked_vote_rows}, got "
                f"{complete_export_unlinked_rows}"
            )

    def align_project_votes_to_reconstructable_ballots(
        self, projects_df, vote_rows_df
    ):
        linked_counts = vote_rows_df.groupby("project_id").size().to_dict()
        projects_df = projects_df.copy()
        projects_df["votes"] = (
            projects_df["project_id"].map(linked_counts).fillna(0).astype(int)
        )
        return projects_df

    def validate_output_vote_totals(self, projects_df, grouped_votes_df):
        exploded_votes = grouped_votes_df.assign(
            project_id=grouped_votes_df["vote"].str.split(",")
        ).explode("project_id")
        counted = exploded_votes.groupby("project_id").size()
        output_counts = projects_df.set_index("project_id")["votes"].astype(int)
        counted = counted.reindex(output_counts.index, fill_value=0)
        if not counted.equals(output_counts):
            differences = output_counts - counted
            raise RuntimeError(
                "Budapest output project totals do not match VOTES: "
                f"{differences[differences != 0].to_dict()}"
            )

    def start(self):
        self.logger.info("Running Budapest preprocessing...")
        projects_df = self.load_projects()
        raw_votes_df, linked_vote_rows_df, grouped_votes_df = self.load_votes(
            projects_df
        )
        complete_vote_rows_df = self.load_complete_vote_rows(projects_df)
        self.validate(
            projects_df,
            raw_votes_df,
            linked_vote_rows_df,
            grouped_votes_df,
            complete_vote_rows_df,
        )
        projects_df = self.align_project_votes_to_reconstructable_ballots(
            projects_df, linked_vote_rows_df
        )
        self.validate_output_vote_totals(projects_df, grouped_votes_df)

        projects_df.to_excel(self.get_output_path(self.projects_excel), index=False)
        grouped_votes_df.to_excel(self.get_output_path(self.votes_excel), index=False)

        self.logger.info(
            "Budapest preprocessing finished: "
            f"{len(projects_df)} projects, {len(grouped_votes_df)} reconstructable "
            f"ballots, {len(linked_vote_rows_df)} linked selections, "
            f"PROJECTS.votes reduced by {self.expected_unlinked_vote_rows} "
            "unlinked official selections."
        )
