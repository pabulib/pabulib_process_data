from __future__ import annotations

from dataclasses import dataclass

from process_data.cities.poznan.postprocess import register_poznan_postprocess
from process_data.get_projects_excel import GetProjects as ExcelGetProjects


@dataclass(kw_only=True)
class GetProjects(ExcelGetProjects):
    def start(self):
        register_poznan_postprocess(
            country=self.country,
            unit=self.unit,
            instance=int(self.instance),
        )
        return super().start()
