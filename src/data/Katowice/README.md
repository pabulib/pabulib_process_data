1. Need to add VLOOKUP into Excel file to have `DZIELNICA` in projects file (`BO Katowice 202X - glosowanie.xlsx`)
2. Processed data will be without project votes (as only scores values in source data).  Then `modify_pb_files` adding votes `update_projects_votes`.

For 2026, the anonymized ballots identify projects by title rather than project ID.
The preprocessor matches title and district to the official results, validates every
project score against the sum of ballot points, and adds project IDs before export.
