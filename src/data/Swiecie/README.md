Świecie data notes
==================

The city provides project results in PDF files and ballot-level data in Excel
files. Project names in ballots are stored as a single comma-separated text
field, but some project names themselves contain commas. The preprocessing code
therefore detects projects by matching full normalized project names from the
PDF against the whole ballot text, not by splitting on commas.

The 2023 reference file has project `c14` with 92 votes. Both `Wyniki-2024.pdf`
and `Glosy_2024.xlsx` give 93 valid indications for that project, so the
generated 2023 output keeps the official/source value 93.

The Excel files also include voters' dates of birth, locality, voting method,
and vote status. Generated VOTES include age calculated on the last day of
voting, neighborhood from the source locality field, and voting_method. A few
source birthdates are impossible historical years, so their age is left blank.
