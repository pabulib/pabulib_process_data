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
- any mismatch between those sources should stay visible and be documented,
- only add city-specific recomputation when we are sure the ballots are the
  authoritative final source.

For new cities, make this choice explicit in city settings instead of relying on
implicit behavior.
