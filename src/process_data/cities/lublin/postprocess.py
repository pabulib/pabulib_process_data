from __future__ import annotations

import atexit
import csv
from pathlib import Path

from pabulib.checker import flds

import helpers.utilities as utils

CITYWIDE_COMMENT = (
    "#1: Lublin's citywide budget was split into two pools: 'hard' for "
    "infrastructural projects and 'soft' for non-infrastructural projects. "
    "Each voter had two citywide votes and could use both on 'hard', both "
    "on 'soft', or split them between the two pools. This hard/soft "
    "distinction was not indicated to voters during voting and only "
    "mattered during tallying. "
    "#2: Initially, 6,900,000 PLN was allocated to citywide projects, with "
    "30% reserved for 'soft' projects (2,070,000 PLN) and 70% for 'hard' "
    "projects (4,830,000 PLN). After the district results were finalized, "
    "the actual district allocation was 7,887,385 PLN, leaving 7,112,615 "
    "PLN for citywide projects. The city then set the final citywide "
    "budgets to 2,133,785 PLN for 'soft' projects and 4,978,830 PLN for "
    "'hard' projects. "
    "#3: Due to an error in the voting system, one citywide ballot "
    "(voter_id 23819) was incorrectly merged into a single vote with four "
    "citywide projects: two 'hard' and two 'soft', instead of at most two "
    "citywide projects in total. The city counted these indications, so for "
    "consistency with the official project totals we also keep them in the "
    "dataset. This did not affect the election outcome."
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


def _infer_citywide_pool(path: Path) -> str | None:
    name_upper = path.name.upper()
    if "_CITYWIDE_HARD" in name_upper:
        return "hard"
    if "_CITYWIDE_SOFT" in name_upper:
        return "soft"
    return None


def fix_district_descriptions(country: str, unit: str, instance: int, **_) -> None:
    base_path = Path("src/output")
    pattern = f"{country}_{unit}_{instance}_*.pb"

    for path in base_path.glob(pattern):
        if "CITYWIDE" in path.name.upper():
            continue
        meta, projects, votes, _, _ = utils.load_pb_file(str(path))
        district = meta.get("district", "")
        if not district:
            continue
        fixed_meta = dict(meta)
        fixed_meta["description"] = f"District PB in {unit}, {district}"
        _write_pb(path, fixed_meta, projects, votes)


def fix_citywide_meta(country: str, unit: str, instance: int, **_) -> None:
    base_path = Path("src/output")
    pattern = f"{country}_{unit}_{instance}_*CITYWIDE_*.pb"

    for path in base_path.glob(pattern):
        meta, projects, votes, _, _ = utils.load_pb_file(str(path))
        pool = _infer_citywide_pool(path)
        if pool is None:
            continue

        fixed_meta = dict(meta)
        fixed_meta["description"] = f"Municipal PB in {unit} | {pool}"
        fixed_meta["subunit"] = pool
        fixed_meta["instance"] = int(instance)
        fixed_meta["num_projects"] = len(projects)
        fixed_meta["num_votes"] = len(votes)
        fixed_meta["comment"] = CITYWIDE_COMMENT
        fixed_meta.pop("district", None)

        _write_pb(path, fixed_meta, projects, votes)


def run_lublin_postprocess(country: str, unit: str, instance: int) -> None:
    fix_district_descriptions(country=country, unit=unit, instance=instance)
    fix_citywide_meta(country=country, unit=unit, instance=instance)


def register_lublin_postprocess(country: str, unit: str, instance: int) -> None:
    if getattr(register_lublin_postprocess, "_registered", False):
        return

    atexit.register(
        run_lublin_postprocess,
        country=country,
        unit=unit,
        instance=int(instance),
    )
    register_lublin_postprocess._registered = True
