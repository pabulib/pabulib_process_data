# Olsztyn 2027

The anonymized ballot export is stored as
`src/data/Olsztyn/2027/Olsztyn_2027_votes_source.xlsx`.

The preprocessing step downloads the official project results from
https://glosujobo.olsztyn.eu/wyniki and joins ballot indications to projects by
the number at the beginning of each `Nr projektów` entry (`Nr <id>.`). It fails
if the official project set or any per-project vote total differs from the
ballot export.

Although voting took place in June 2026, this is OBO 2027: the selected
projects are intended for implementation in 2027.

The initial published budget was PLN 9,000,000 (PLN 3,000,000 citywide and PLN
6,000,000 for neighborhoods). The official result page marks projects totaling
PLN 9,010,530 as selected. For neighborhood outputs where selected project
costs exceed the initial neighborhood limit, metadata uses the selected cost as
the effective budget and records that adjustment in a comment.
