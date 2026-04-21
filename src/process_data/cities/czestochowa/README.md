2024, used comments:
* comment;#1: The cost of Project 237 was exceeding the district budget (546 000), which should not have happened. Unfortunately, it was eligible to be voted on; therefore, we reduced its cost to align with the budget (542 052). (Wrzosowiak)
* comment;#1: If there are unused funds remaining in any district or the citywide budget, they are aggregated and allocated to the district with the highest turnout. Therefore, we adjusted the budget from 194 431 to 236 277. (Kiedrzyn)
* comment;#1: Project 586 was free (cost 0). To keep data consistent and not to have 0-cost projects (may cause problems when processing data) we set its cost to an artificial value of 1. (Częstochówka-Parkitka)

2020 audit:
* `src/process_data/cities/czestochowa/audit_2020_ballots.py` re-checks the raw XLS ballots against the current `2020` outputs.
* The raw file has `50 758` project indications, while the current outputs use `49 797` and still match the official project-level `votes` and `score` exactly.
* A deterministic re-match can raise the number of resolvable raw indications to `50 131`, but doing so would make at least `118` projects exceed the official totals.
* Conclusion: the remaining gap is not just a weak matcher. The raw XLS and the official final results are not fully reconcilable, so the current `2020` outputs should stay unchanged unless a better authoritative source appears.
