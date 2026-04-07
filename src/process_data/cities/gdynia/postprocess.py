from __future__ import annotations

import atexit
import csv
from pathlib import Path

from pabulib.checker import flds

import helpers.utilities as utils

GREEN_BUDGET_SUBUNIT = "Green Budget"
ONLINE_ONLY_VOTING_INSTANCES = {2020, 2021, 2022, 2023, 2024, 2025}
CITYWIDE_OUTPUTS = {
    2021: {
        "GENERAL": {
            "filename": "",
            "description": "Municipal PB in Gdynia",
            "subunit": None,
            "budget": 1000517,
        },
        "KBO": {
            "filename": "GREEN_BUDGET",
            "description": "Municipal PB in Gdynia, Green Budget",
            "subunit": GREEN_BUDGET_SUBUNIT,
            "budget": 1000000,
        },
    },
    2022: {
        "KBO": {
            "filename": "GREEN_BUDGET",
            "description": "Municipal PB in Gdynia, Green Budget",
            "subunit": GREEN_BUDGET_SUBUNIT,
            "budget": 2094548,
        }
    },
    2023: {
        "KBO": {
            "filename": "GREEN_BUDGET",
            "description": "Municipal PB in Gdynia, Green Budget",
            "subunit": GREEN_BUDGET_SUBUNIT,
            "budget": 2000000,
        }
    },
    2024: {
        "JBO": {
            "filename": "",
            "description": "Municipal PB in Gdynia",
            "subunit": None,
            "budget": 1000000,
        },
        "KBO": {
            "filename": "GREEN_BUDGET",
            "description": "Municipal PB in Gdynia, Green Budget",
            "subunit": GREEN_BUDGET_SUBUNIT,
            "budget": 2000000,
        },
    },
    2025: {
        "JBO": {
            "filename": "",
            "description": "Municipal PB in Gdynia",
            "subunit": None,
            "budget": 1000000,
        },
        "KBO": {
            "filename": "GREEN_BUDGET",
            "description": "Municipal PB in Gdynia, Green Budget",
            "subunit": GREEN_BUDGET_SUBUNIT,
            "budget": 1000000,
        },
    },
}
COMMENT_SELECTED_2 = (
    "Projects marked with selected=2 were funded as additional turnout-award "
    'projects under Gdynia\'s "Projekt +1" rule: one extra large project and '
    "two extra small projects are implemented in the districts with the highest "
    "voting turnout, using city funds outside the regular BO allocation."
)
PROJECT_ORDER_OVERRIDES = {
    "Poland_Gdynia_2024_SRODMIESCIE_LARGE.pb": [
        "2024/SRO/0009",
        "2024/SRO/0018",
    ],
}


def _ordered_fields(fields: list[str], order: list[str]) -> list[str]:
    return [field for field in order if field in fields]


def _write_pb(path: Path, meta: dict, projects: dict, votes: dict) -> None:
    if not projects:
        raise RuntimeError(f"No projects to write for {path}")

    project_fields = _ordered_fields(
        list(next(iter(projects.values())).keys()), flds.PROJECTS_FIELDS_ORDER
    )

    if votes:
        vote_fields = _ordered_fields(
            ["voter_id", *list(next(iter(votes.values())).keys())], flds.VOTES_FIELDS_ORDER
        )
    else:
        vote_fields = ["voter_id", "vote"]

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


def _normalize_meta(meta: dict, projects: dict, votes: dict) -> dict:
    fixed_meta = dict(meta)
    fixed_meta["num_projects"] = len(projects)
    fixed_meta["num_votes"] = len(votes)
    fixed_meta["min_length"] = 1
    fixed_meta["max_length"] = min(3, len(projects))

    comments = []
    if 2 in _selected_values(projects):
        comments.append(COMMENT_SELECTED_2)

    if comments:
        fixed_meta["comment"] = " ".join(
            f"#{idx}: {comment}" for idx, comment in enumerate(comments, 1)
        )
    else:
        fixed_meta.pop("comment", None)

    return fixed_meta


def _apply_overrides(path: Path, meta: dict) -> dict:
    return dict(meta)


def _reorder_projects(path: Path, projects: dict) -> dict:
    preferred_order = PROJECT_ORDER_OVERRIDES.get(path.name)
    if not preferred_order:
        return projects

    reordered = {}
    used = set()

    for project_id in preferred_order:
        if project_id in projects:
            reordered[project_id] = projects[project_id]
            used.add(project_id)

    for project_id, project_data in projects.items():
        if project_id not in used:
            reordered[project_id] = project_data

    return reordered


def _apply_fully_funded(meta: dict, projects: dict) -> dict:
    fixed_meta = dict(meta)
    total_cost = sum(float(project.get("cost", 0)) for project in projects.values())
    budget = float(fixed_meta.get("budget", 0))
    if budget >= total_cost:
        fixed_meta["fully_funded"] = 1
    else:
        fixed_meta.pop("fully_funded", None)
    return fixed_meta


def _apply_online_voting_method(votes: dict, instance: int) -> dict:
    if int(instance) not in ONLINE_ONLY_VOTING_INSTANCES:
        return votes

    fixed_votes = {}
    for voter_id, vote_data in votes.items():
        updated_vote = dict(vote_data)
        updated_vote["voting_method"] = "internet"
        fixed_votes[voter_id] = updated_vote
    return fixed_votes


def _split_citywide_vote(vote: str, pool_mapping: dict[str, str], pool_name: str) -> str:
    if not vote:
        return ""
    selected = [
        project_id
        for project_id in str(vote).split(",")
        if pool_mapping.get(project_id) == pool_name
    ]
    return ",".join(selected)


def split_citywide_file(country: str, unit: str, instance: int, **_) -> None:
    root_path = Path("src/output") / f"{country}_{unit}_{instance}_.pb"
    if not root_path.exists():
        return

    meta, projects, votes, _, _ = utils.load_pb_file(str(root_path))
    pool_mapping = utils.name_and_load_dict_as_json(
        country, unit, instance, "project_citywide_pool_mapping"
    )
    output_config = CITYWIDE_OUTPUTS[int(instance)]

    citywide_projects = {}
    for pool_name in output_config:
        citywide_projects[pool_name] = {
            project_id: project
            for project_id, project in projects.items()
            if pool_mapping.get(project_id) == pool_name
        }

    citywide_votes = {pool_name: {} for pool_name in output_config}
    for voter_id, vote_data in votes.items():
        for pool_name in output_config:
            split_vote = _split_citywide_vote(vote_data.get("vote", ""), pool_mapping, pool_name)
            if not split_vote:
                continue
            new_vote_data = dict(vote_data)
            new_vote_data["vote"] = split_vote
            citywide_votes[pool_name][voter_id] = new_vote_data

    for pool_name, config in output_config.items():
        pool_projects = citywide_projects[pool_name]
        pool_votes = _apply_online_voting_method(citywide_votes[pool_name], instance)
        if not pool_projects:
            continue

        pool_meta = _normalize_meta(meta, pool_projects, pool_votes)
        pool_meta["description"] = config["description"]
        pool_meta["budget"] = config["budget"]
        pool_meta["rule"] = "greedy-no-skip"
        pool_meta.pop("district", None)
        if config["subunit"] is None:
            pool_meta.pop("subunit", None)
        else:
            pool_meta["subunit"] = config["subunit"]
        pool_meta = _apply_fully_funded(pool_meta, pool_projects)
        suffix = config["filename"]
        output_path = (
            root_path
            if not suffix
            else Path("src/output") / f"{country}_{unit}_{instance}_{suffix}.pb"
        )
        _write_pb(output_path, pool_meta, pool_projects, pool_votes)

    if all(config["filename"] for config in output_config.values()) and root_path.exists():
        root_path.unlink()


def fix_local_meta(country: str, unit: str, instance: int, **_) -> None:
    base_path = Path("src/output")
    pattern = f"{country}_{unit}_{instance}_*.pb"

    for path in base_path.glob(pattern):
        meta, projects, votes, _, _ = utils.load_pb_file(str(path))
        projects = _reorder_projects(path, projects)
        votes = _apply_online_voting_method(votes, instance)
        fixed_meta = _normalize_meta(meta, projects, votes)
        fixed_meta = _apply_overrides(path, fixed_meta)
        _write_pb(path, fixed_meta, projects, votes)


def fix_generic_files(country: str, unit: str, instance: int, **_) -> None:
    base_path = Path("src/output")
    paths = list(base_path.glob(f"{country}_{unit}_{instance}_*.pb"))
    root_path = base_path / f"{country}_{unit}_{instance}_.pb"
    if root_path.exists() and root_path not in paths:
        paths.append(root_path)

    for path in paths:
        meta, projects, votes, _, _ = utils.load_pb_file(str(path))
        projects = _reorder_projects(path, projects)
        votes = _apply_online_voting_method(votes, instance)
        fixed_meta = _normalize_meta(meta, projects, votes)
        fixed_meta = _apply_fully_funded(fixed_meta, projects)
        fixed_meta = _apply_overrides(path, fixed_meta)
        _write_pb(path, fixed_meta, projects, votes)


def fix_citywide_meta(country: str, unit: str, instance: int, **_) -> None:
    for config in CITYWIDE_OUTPUTS[int(instance)].values():
        suffix = config["filename"]
        path = (
            Path("src/output") / f"{country}_{unit}_{instance}_.pb"
            if not suffix
            else Path("src/output") / f"{country}_{unit}_{instance}_{suffix}.pb"
        )
        if not path.exists():
            continue

        meta, projects, votes, _, _ = utils.load_pb_file(str(path))
        projects = _reorder_projects(path, projects)
        votes = _apply_online_voting_method(votes, instance)
        fixed_meta = _normalize_meta(meta, projects, votes)
        fixed_meta["description"] = config["description"]
        fixed_meta["budget"] = config["budget"]
        fixed_meta["rule"] = "greedy-no-skip"
        fixed_meta.pop("district", None)
        if config["subunit"] is None:
            fixed_meta.pop("subunit", None)
        else:
            fixed_meta["subunit"] = config["subunit"]
        fixed_meta = _apply_fully_funded(fixed_meta, projects)
        fixed_meta = _apply_overrides(path, fixed_meta)
        _write_pb(path, fixed_meta, projects, votes)

    for stale_name in ("KBO", "JBO"):
        stale_path = Path("src/output") / f"{country}_{unit}_{instance}_{stale_name}.pb"
        if stale_path.exists():
            stale_path.unlink()


def run_gdynia_postprocess(country: str, unit: str, instance: int) -> None:
    if int(instance) not in ONLINE_ONLY_VOTING_INSTANCES:
        return
    if int(instance) in CITYWIDE_OUTPUTS:
        split_citywide_file(country=country, unit=unit, instance=instance)
        fix_local_meta(country=country, unit=unit, instance=instance)
        fix_citywide_meta(country=country, unit=unit, instance=instance)
    else:
        fix_generic_files(country=country, unit=unit, instance=instance)


def register_gdynia_postprocess(country: str, unit: str, instance: int) -> None:
    if int(instance) not in ONLINE_ONLY_VOTING_INSTANCES:
        return
    if getattr(register_gdynia_postprocess, "_registered", False):
        return

    atexit.register(
        run_gdynia_postprocess,
        country=country,
        unit=unit,
        instance=int(instance),
    )
    register_gdynia_postprocess._registered = True
