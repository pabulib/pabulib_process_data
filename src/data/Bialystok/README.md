Bialystok data notes
====================

2027
----

The city provided anonymized ballot data in response to a public information
request. The official project rankings are published by the city at:

https://www.bialystok.pl/pl/aktualnosci/wyniki-glosowania-na-budzet-obywatelski-2027.html

The preprocessor reads project metadata, official totals, and selection status
from the official ranking document. It counts project indications from valid
ballots and requires every count to match the official total before writing the
processed files. Age `0` in the ballot source means that age was unavailable
and is stored as a missing value.

The output is split into the citywide, local, and school project pools, with
budgets of 8,000,000 PLN, 4,000,000 PLN, and 3,000,000 PLN respectively.
