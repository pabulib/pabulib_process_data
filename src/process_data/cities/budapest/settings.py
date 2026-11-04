all_data = {
    2025: {
        "base_data": {
            "country": "Hungary",
            "unit": "Budapest",
            "instance": 2025,
        },
        "preprocess": {
            "data_dir": "2025",
            "projects_source_excel": "List of projects for 2025 correct",
            "votes_source_excel": "Anonymized vote-level data for 2025",
            "complete_selections_source_excel": (
                "Anonymized vote-level data for 2025 correct"
            ),
            "projects_excel": "Budapest_2025_projects_processed",
            "votes_excel": "Budapest_2025_votes_processed",
            "project_vote_totals_source": "reconstructable_ballots",
            "expected_unknown_project_rows": 5,
            "expected_unlinked_vote_rows": 36,
            "expected_repeated_project_rows": 3,
        },
        "get_projects": {
            "data_dir": "2025",
            "excel_filename": "Budapest_2025_projects_processed",
            "columns_mapping": {
                "project_id": "project_id",
                "name": "name",
                "cost": "cost",
                "votes": "votes",
                "category": "category",
                "selected": "selected",
                "latitude": "latitude",
                "longitude": "longitude",
            },
        },
        "get_votes": {
            "data_dir": "2025",
            "excel_filename": "Budapest_2025_votes_processed",
            "only_valid_votes": True,
            "voter_id_integer": False,
            "columns_mapping": {
                "voter_id": "voter_id",
                "voting_method": "voting_method",
                "votes_columns": {
                    "unit": "vote",
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
        },
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "category",
                "selected",
                "latitude",
                "longitude",
            ],
        },
        "votes_data": {
            "unit_fields": ["voter_id", "vote", "voting_method"],
        },
        "metadata": {
            "vote_type": "approval",
            "rule": "greedy-custom",
            "date_begin": "01.09.2025",
            "date_end": "30.09.2025",
            "min_length": "1",
            "max_length": "15",
            "max_length_per_category": "3",
            "edition": "5",
            "language": "hu",
            "currency": "HUF",
            "categories": (
                "Local Small Idea,Local Big Idea,Green,Open,Social"
            ),
            "comment": [
                "Each voter could approve at most 3 projects in each category.",
                "The official outcome used a custom category-based greedy rule. "
                "Projects were ranked by their combined online and offline "
                "approval totals within five category budgets: 120 million HUF "
                "each for Social, Open, and Green, 400 million HUF for Local "
                "Small Idea, and 240 million HUF for Local Big Idea. Selection "
                "within a category stopped when the next ranked project did not "
                "fit. From the combined 50 million HUF left in the category "
                "budgets, project 681 was then funded for 20 million HUF, and "
                "the remaining 30 million HUF was kept as a reserve.",
                "This dataset contains online votes only. The 9,946 offline "
                "approvals (approximately 7% of all approvals) are not included "
                "in VOTES. Therefore, the official winners indicated by "
                "selected=1 were not determined exclusively by VOTES.",
                "The city corrected the project file after the initial response "
                "because the original file contained incorrect vote totals. We "
                "use the corrected file for project attributes and the official "
                "outcome.",
                "Five rows in the original vote-level file referred to projects "
                "outside the corrected 2025 project list and were omitted.",
                "The city reported that 36 additional online selections cannot be "
                "linked to individual ballots because the corresponding user "
                "accounts were deleted. To keep PROJECTS and VOTES internally "
                "consistent, PROJECTS.votes was calculated from the reconstructable "
                "ballots. Its total is 137,750, which is 36 lower than the official "
                "online total of 137,786.",
                "Three ballots contain a repeated project selection. The "
                "repetitions are present in the city data and were retained.",
            ],
            "acknowledgments": "File assembled by A. Stankovics",
        },
    },
}
