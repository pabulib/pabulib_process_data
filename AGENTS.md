# Repository Notes For Codex

## Dual-source election data

Some cities provide two separate sources:

- a projects/results sheet with official per-project totals,
- a votes sheet with anonymized individual ballots.

When these two sources disagree, do not silently recompute project-level
`votes` or `score` from the ballots and overwrite the official project results.

Preferred rule:

- `PROJECTS` should follow the official projects/results source,
- `VOTES` should follow the anonymized votes source,
- there cannot be any mismatch between those sources. so if any, we need to investigate
- only add city-specific recomputation when we are sure the ballots are the
  authoritative final source.

For new cities, make this choice explicit in city settings instead of relying on
implicit behavior.

## Metadata comments

When adding metadata comments, prefer short, case-specific notes modeled on
existing Pabulib comments:

- https://pabulib.org/details

For budget adjustments, prefer direct wording such as `the city increased the
budget from X to Y`, or `the budget was increased from X to Y`, instead of
abstract phrasing like `the city clarified that the project pool was increased`.
Good examples on the Details page include comments starting with `Initially,
the budget...` or `If there are unused funds... Therefore, we adjusted the
budget...`.

Avoid boilerplate comments such as saying that `PROJECTS` were reconstructed
from ballots or matched from another source, unless the user explicitly asks for
that wording.

## Pabulib format reference

Use the official format page as the reference when deciding how to encode
non-standard outcomes:

- https://pabulib.org/format

The `.pb` file has `META`, `PROJECTS`, and `VOTES` sections separated with
semicolon-delimited CSV-style rows. The `selected` field is integer-coded: `1`
means selected, `0` means not selected, and other values such as `2` may be used
for special cases only when the case is explained in a metadata comment.
