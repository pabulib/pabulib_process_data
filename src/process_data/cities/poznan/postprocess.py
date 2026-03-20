from __future__ import annotations

import atexit
import csv
from pathlib import Path

from pabulib.checker import flds

import helpers.utilities as utils
from process_data.cities.poznan.budgets import budgets

COMMENT_SELECTED_2 = (
    "This special greedy rule works as follows: At the beginning, we sort "
    "projects based on the number of votes. Then, we fund projects that "
    "received the highest number of votes until the next project on the list "
    "does not fit within the budget. Finally, if the remaining budget is "
    "enough to fund at least 80% of that project, we fund it as well with "
    "the external reserve funds (for example, the unused funds remaining in "
    "other districts). We mark such project with number 2 in the selected "
    "column"
)

COMMENT_SELECTED_3 = (
    "Sometimes, additional funds (for example, unused funds from other "
    "districts) are allocated to a district. These funds are used to finance "
    "the highest-voted projects that have not yet been selected. We mark "
    "such projects with number 3 in the selected column"
)


def _ordered_fields(fields: list[str], order: list[str]) -> list[str]:
    return [field for field in order if field in fields]


def _write_pb(path: Path, meta: dict, projects: dict, votes: dict) -> None:
    project_fields = _ordered_fields(
        list(next(iter(projects.values())).keys()), flds.PROJECTS_FIELDS_ORDER
    )
    vote_fields = _ordered_fields(
        ["voter_id", *list(next(iter(votes.values())).keys())], flds.VOTES_FIELDS_ORDER
    )

    with path.open("w", newline="", encoding="utf-8") as file_:
        writer = csv.writer(file_, delimiter=";")

        writer.writerow(["META"])
        writer.writerow(["key", "value"])
        for key in flds.META_FIELDS_ORDER:
            if key in meta:
                writer.writerow([key, meta[key]])

        writer.writerow(["PROJECTS"])
        writer.writerow(project_fields)
        for project in projects.values():
            writer.writerow([project.get(field, "") for field in project_fields])

        writer.writerow(["VOTES"])
        writer.writerow(vote_fields)
        for voter_id, vote_data in votes.items():
            row = []
            for field in vote_fields:
                if field == "voter_id":
                    row.append(voter_id)
                else:
                    row.append(vote_data.get(field, ""))
            writer.writerow(row)


def _selected_values(projects: dict) -> set[int]:
    values = set()
    for project in projects.values():
        try:
            values.add(int(project.get("selected", 0)))
        except (TypeError, ValueError):
            continue
    return values


def _apply_comment_policy(meta: dict, projects: dict) -> dict:
    fixed_meta = dict(meta)
    comments = [COMMENT_SELECTED_2]
    if 3 in _selected_values(projects):
        comments.append(COMMENT_SELECTED_3)
    fixed_meta["comment"] = " ".join(
        f"#{idx}: {comment}" for idx, comment in enumerate(comments, 1)
    )
    return fixed_meta


def _infer_citywide_size(path: Path, meta: dict) -> str | None:
    name_upper = path.name.upper()
    if name_upper.endswith("_LARGE.PB"):
        return "large"
    if name_upper.endswith("_SMALL.PB"):
        return "small"

    subunit = str(meta.get("subunit", "")).strip().lower()
    if subunit.endswith("large"):
        return "large"
    if subunit.endswith("small"):
        return "small"
    return None


def fix_comments(country: str, unit: str, instance: int, **_) -> None:
    base_path = Path("src/output")
    pattern = f"{country}_{unit}_{instance}_*.pb"

    for path in base_path.glob(pattern):
        meta, projects, votes, _, _ = utils.load_pb_file(str(path))
        fixed_meta = _apply_comment_policy(meta, projects)
        _write_pb(path, fixed_meta, projects, votes)


def fix_citywide_meta(country: str, unit: str, instance: int, **_) -> None:
    base_path = Path("src/output")
    pattern = f"{country}_{unit}_{instance}_*CITYWIDE_*.pb"

    for path in base_path.glob(pattern):
        meta, projects, votes, _, _ = utils.load_pb_file(str(path))
        citywide_size = _infer_citywide_size(path, meta)
        if citywide_size is None:
            continue

        fixed_meta = _apply_comment_policy(meta, projects)
        fixed_meta["description"] = f"Municipal PB in {unit} | {citywide_size}"
        fixed_meta["subunit"] = citywide_size
        fixed_meta["instance"] = int(instance)
        fixed_meta["num_projects"] = len(projects)
        fixed_meta["num_votes"] = len(votes)
        fixed_meta.pop("district", None)

        try:
            fixed_meta["budget"] = budgets[int(instance)]["_CITYWIDE"][citywide_size]
        except KeyError:
            pass

        _write_pb(path, fixed_meta, projects, votes)


def fix_green_budget_meta(country: str, unit: str, instance: int, **_) -> None:
    base_path = Path("src/output")
    pattern = f"{country}_{unit}_{instance}_*ZIELONY_BUDZET*.pb"

    for path in base_path.glob(pattern):
        meta, projects, votes, _, _ = utils.load_pb_file(str(path))

        fixed_meta = _apply_comment_policy(meta, projects)
        fixed_meta["description"] = f"Municipal PB in {unit}, Green Budget"
        fixed_meta["subunit"] = "Green Budget"
        fixed_meta["instance"] = int(instance)
        fixed_meta["num_projects"] = len(projects)
        fixed_meta["num_votes"] = len(votes)
        fixed_meta.pop("district", None)

        _write_pb(path, fixed_meta, projects, votes)


def run_poznan_postprocess(country: str, unit: str, instance: int) -> None:
    fix_comments(country=country, unit=unit, instance=instance)
    fix_citywide_meta(country=country, unit=unit, instance=instance)
    fix_green_budget_meta(country=country, unit=unit, instance=instance)


def register_poznan_postprocess(country: str, unit: str, instance: int) -> None:
    if getattr(register_poznan_postprocess, "_registered", False):
        return

    atexit.register(
        run_poznan_postprocess,
        country=country,
        unit=unit,
        instance=int(instance),
    )
    register_poznan_postprocess._registered = True
