Radom data notes
================

2026
----

The city provided project-level final results, online project-point records,
and aggregate paper point counts in response to the 2026 public information
request. The city stated that it does not store ballot-level data for this
voting system.

The generated VOTES section therefore contains one synthetic row for each
project-point entry, not one row per original ballot. If one real voter assigned
points to two projects, those two project-point entries cannot be linked in the
source data and are represented as two separate synthetic voter ids.

The official winner list contains three budget categories:

- projects up to 100,000 PLN,
- projects from 100,000 to 600,000 PLN,
- projects above 600,000 PLN.

The official results also list projects funded from unused money pooled across
the three categories. These additional projects are marked with `selected=2`:
project 32 in the small-project category and projects 114 and 124 in the
medium-project category.

Sources:

- https://www.radom.pl/aktualnosci/poznalismy-wyniki-glosowania-na-projekty-zgloszone-do-budzetu-obywatelskiego/
- https://konsultacje.radom.pl/wyniki-glosowania-budzet-obywatelski-2026/
