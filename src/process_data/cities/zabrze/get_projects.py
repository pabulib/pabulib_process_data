from dataclasses import dataclass

from process_data.get_projects_excel import GetProjects as BaseGetProjects


@dataclass(kw_only=True)
class GetProjects(BaseGetProjects):
    preserve_official_results: bool = False

    def __post_init__(self):
        if not self.preserve_official_results:
            raise RuntimeError(
                "Zabrze: official project results must be preserved explicitly."
            )
        return super().__post_init__()

    @staticmethod
    def exact_cost(value):
        value = round(float(value), 2)
        return int(value) if value.is_integer() else value

    def iterate_through_projects(self):
        super().iterate_through_projects()

        # ProjectItem rounds costs to whole PLN. Zabrze publishes two projects
        # with grosz amounts, so restore their exact official costs here.
        exact_costs = {}
        for row_index in range(1, self.sheet.nrows):
            row = self.sheet.row_values(row_index)
            project_id = str(row[self.col["project_id"]]).strip()
            votes = row[self.col["votes"]]
            cost = row[self.col["cost"]]
            if project_id in ("", "NULL") or votes == "" or cost == "":
                continue
            exact_costs[project_id] = self.exact_cost(cost)

        for projects in self.projects_data_per_district.values():
            for project in projects:
                project_id = str(project["project_id"])
                project["cost"] = exact_costs[project_id]
