# Budapest

## 2025

The processing uses four source files:

- `List of projects for 2025.xlsx` is the original project list. The city later
  stated that its vote totals were incorrect, so it is retained only as source
  documentation.
- `List of projects for 2025 correct.xlsx` is the corrected official project
  list. It supplies project details, official online totals, offline totals, and
  the official outcome.
- `Anonymized vote-level data for 2025.xlsx` contains stable anonymized voter
  identifiers and is the source for the reconstructable ballots in `VOTES`.
- `Anonymized vote-level data for 2025 correct.xlsx` contains all 137,786 online
  selections, but assigns them to one technical anonymous account. It is used
  only to verify the official project totals and identify the selections absent
  from the reconstructable ballots.

The city sent the corrected project list on 2026-06-15. The accompanying letter
states that the original project file had incorrect vote totals and that the
corrected file should be used instead.

`VOTES` is based on the anonymized online vote-level file. The vote-level file
contained five rows for project IDs that are not present in the corrected 2025
project list; those rows were omitted.

The city later confirmed that 36 online selections cannot be linked to their
individual ballots because the corresponding user accounts were deleted. We do
not create synthetic voters for these selections. The later complete export
assigns every selection to one technical anonymous account and is used only to
verify the project totals and the 36-row difference. `PROJECTS.votes` therefore
is recalculated from the reconstructable ballots so that it remains internally
consistent with `VOTES`. Its total is 137,750, which is 36 lower than the
official online total of 137,786. `PROJECTS.selected` continues to follow the
official outcome, which also took 9,946 offline approvals into account. `VOTES`
contains the 15,010 reconstructable online ballots.

Three reconstructed ballots contain a repeated project selection. These rows
are also present in the city's later complete selection-level export and are
retained so that `VOTES` follows the supplied anonymized ballot source.

Category names follow the English labels used in the municipal Budapest 2024
Pabulib file: `Local Small Idea`, `Local Big Idea`, `Green`, `Open`, and
`Social`.

The decision rule is encoded as `greedy-custom`. The official outcome first
used separate category budgets: 120 million HUF each for `Social`, `Open`, and
`Green`, 400 million HUF for `Local Small Idea`, and 240 million HUF for
`Local Big Idea`. Projects were ranked by their combined online and offline
approval totals within each category, and selection in a category stopped when
the next ranked project did not fit. This left 50 million HUF across the
category budgets. Project 681, with a cost of 20 million HUF, was subsequently
funded from those combined remainders, and the remaining 30 million HUF became
a reserve. The official winning projects therefore cannot be reproduced by a
single ordinary `greedy` or `greedy-no-skip` pass over the citywide budget.

Official rule sources:

- [Budapest participatory-budgeting rules](https://otlet.budapest.hu/oldal/bovebben-a-kozossegi-koltsegvetesrol)
- [Official 2024/2025 winner proposal and decision](https://budapest.hu/api/file/doc/e01-fpm-dontes-kk-nyertes-otletek-2024-2025-vegleges-1-.pdf)
- [Budapest announcement of the 2025 results](https://budapest.hu/hirek/2025/10/13/elerhetoek-a-fovarosi-kozossegi-koltsegvetes-uj-nyertes-otletei)
