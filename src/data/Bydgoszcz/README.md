# Bydgoszcz 2025

The city provided anonymized vote-level data on 2026-06-18 in response to a
public information request. The public BBO results protocol is used for project
numbers, costs, selected status, and budgets.

The vote-level export contains 56,825 rows: 56,700 accepted votes and 125
rejected votes. The official protocol reports 56,702 valid votes. The two
differences are:

- project 466, `Naukowe place zabaw na Szwederowie`: 173 accepted rows in the
  vote-level file, 174 votes in the protocol;
- project 371, `Festiwal Wodny nad Zalewem Smukalskim`: 198 accepted rows in
  the vote-level file, 199 votes in the protocol.

We did not fabricate the two missing rows. `VOTES` follows the anonymized
vote-level file, and `PROJECTS.votes` follows the included `VOTES` data for
internal consistency.

The protocol prints four pool budgets that are 1-2 PLN lower than the total
cost of the projects marked for implementation. Therefore, the `.pb` metadata
uses the selected-project cost as the budget for Błonie, Bydgoszcz Wschód -
Siernieczek, Flisy, and Okole.

Projects are ranked by votes within each project pool. A project must receive
at least 30 votes to be eligible. The official selections in all 59 pools match
`greedy-no-skip` with `min_project_score_threshold=30`: projects are considered
in ranking order and selection stops when the next eligible project does not
fit the remaining pool budget.

The city results announcement says that 269 projects were put to a vote. The
detailed official protocol and the vote-level export contain 268 project-pool
entries, and those 268 entries reconcile with each other except for the two
missing vote rows described above. The pipeline follows the detailed protocol.
