all_data = {
    # Example configuration for a specific year and city
    2025: {
        # --- General Metadata ---
        "base_data": {
            "country": "Poland",  # Country name, e.g., "Poland"
            "unit": "a_city_template",  # City name, e.g., "Warszawa"
            "instance": 2025,  # Year or unique identifier for this instance
        },
        # --- Project Data Configuration ---
        "get_projects": {
            "data_dir": "2025",  # Directory for storing project data (relative to `data/<city>/`)
            "excel_filename": "sample_projects",  # Excel file name (without extension) containing project data
            "columns_mapping": {  # Maps file column headers to internal keys
                "project_id": "Project ID",  # ID for the project
                "name": "Title",  # Project name/title
                "cost": "Cost",  # Cost of the project
                "votes": "Votes",  # Number of votes for the project
                "district": "District",  # District or neighborhood for the project
                "selected": "Selected",  # Optional: whether the project was selected or not
                # You can add or modify fields based on your data, e.g., "category", "target", etc.
            },
        },
        # --- Vote Data Configuration ---
        "get_votes": {
            "excel_filename": "sample_votes",  # Excel file name (without extension) containing vote data
            "data_dir": "2025",  # Directory for storing vote data (relative to `data/`)
            "only_valid_votes": False,  # Set to True if the file contains only valid votes
            "valid_value": "valid",  # Keyword in the file that marks votes as valid
            "columns_mapping": {  # Maps file column headers to internal keys
                "voter_id": "Voter ID",  # Unique identifier for the voter
                "sex": "Sex",  # Voter's gender
                "age": "Age",  # Voter's age
                "district": "District",  # District or neighborhood for the voter
                "voting_method": "Voting Method",  # How the vote was cast (e.g., online, in person)
                "if_valid": "Vote Status",  # Column marking valid/invalid votes
                "votes_columns": {  # Special mapping for multi-column votes
                    "unit": "Citywide Projects",  # Column for citywide project votes
                    "local": "District Projects",  # Column for district-level project votes
                },
            },
            "rows_iterator_handler": "one_voter_one_row_no_points",
            # Use one of iterators. Created on an ongoing basis depending on needs.
            # You can have one voter per row, or many rows per voter.
            # Just votes, or votes with points? citywide votes in the same row as district ones? etc.
            # Valid options:
            #   "one_voter_one_row_no_points" - Each voter has one row; votes are binary (selected/not selected).
            #   "one_voter_multiple_rows_no_points" - Each voter has multiple rows, one vote per row.
            #   "one_voter_multiple_rows_with_points" - Same as above but includes scoring or ranking points.
            #   "no_points_votes_not_separated" - Votes and districts are combined in a single column.
        },
        # --- Project Fields to Include in `.pb` Files ---
        "projects_data": {
            "unit_fields": [
                "project_id",
                "cost",
                "votes",
                "name",
                "selected",
                # "category",
                # "target",
            ],
            # Specify which project fields should be included in the output `.pb` files.
            # Add additional fields as needed based on your data schema.
        },
        # --- Voter Fields to Include in `.pb` Files ---
        "votes_data": {
            "unit_fields": [
                "voter_id",
                "age",
                "sex",
                "vote",
                "neighborhood",
                "voting_method",
            ],
            "districts_fields": ["voter_id", "age", "sex", "vote", "voting_method"],
            # Define which fields related to voters should be included in `.pb` files.
        },
        # --- Metadata ---
        "metadata": {
            "vote_type": "approval",  # Type of voting system: "approval", "ranked", etc.
            "rule": "greedy",  # Decision rule for allocating budgets (e.g., "greedy", "proportional")
            "date_begin": "01.01.2025",  # Start date of voting (DD.MM.YYYY)
            "date_end": "31.01.2025",  # End date of voting (DD.MM.YYYY)
            "language": "en",  # Language code (ISO 639-1, e.g., "en", "pl")
            "edition": "1",  # Edition of participatory budgeting (e.g., "1", "2025")
            "currency": "PLN",  # Currency used (e.g., "PLN", "USD")
            "unit": {  # Additional metadata for citywide projects
                "max_length": "10",  # Max vote length, different for citywide and district
                "comment": [
                    "Explanation or additional notes for unit-specific metadata"
                ],
            },
            "district": {  # Additional metadata for district-level projects
                "max_length": "15",  # Max vote length, different for citywide and district
                "comment": [
                    "Explanation or additional notes for district-specific metadata"
                ],
            },
        },
    },
    # Add configurations for additional years as needed
}
