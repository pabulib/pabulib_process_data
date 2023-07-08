import collections
import re
from dataclasses import dataclass

import docx
import helpers.utilities as utils
from process_data.base_config import BaseConfig
from process_data.models import ProjectItem
import pdf2docx


@dataclass
class GetProjects(BaseConfig):
    data_dir: str
    projects_docx: str
    columns: dict
    cell_colours: dict
    subdistricts: bool

    def __post_init__(self):
        self.logger = utils.create_logger()
        self.initialize_mapping_dicts()
        self.check_if_pdf()
        return super().__post_init__()

    def check_if_pdf(self):
        path_to_pdf = None
        if self.projects_docx.endswith(".pdf"):
            pdf_name = self.projects_docx.replace(".pdf", "")
            path_to_pdf = utils.get_path_to_excel_file_by_unit(
                pdf_name, self.unit, self.data_dir, "pdf"
            )

            self.path_to_docx = utils.get_path_to_excel_file_by_unit(
                pdf_name, self.unit, self.data_dir, "docx"
            )

            pdf2docx.parse(path_to_pdf, self.path_to_docx)

        else:
            self.path_to_docx = utils.get_path_to_excel_file_by_unit(
                self.projects_docx, self.unit, self.data_dir, "docx"
            )

    def get_cell_colour(self, cell):
        pattern = re.compile('w:fill="(\S*)"')
        match = pattern.search(cell._tc.xml)
        try:
            result = match.group(1)
        except AttributeError:
            result = None
        return result

    def check_if_bold_text(self, cell):
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                if run.bold:
                    return True
                return

    def check_project_id(self, project_id):
        project_id = project_id.strip()
        if "\t" in project_id:
            project_id = project_id.split("\t")[1]
        return project_id

    def get_data_from_docx_table(self, doc):
        for page_no in range(len(doc.tables)):
            table = doc.tables[page_no]
            for i, row in enumerate(table.rows):
                row_values = [cell.text for cell in row.cells]

                # Establish the mapping based on the first row
                # headers; these will become the keys of our dictionary
                if page_no == 0:
                    if i == 0:
                        continue
                    elif i == 1:
                        values = [cell.text.replace("\n", "")
                                  for cell in row.cells]
                        keys = [self.columns.get(value, value)
                                for value in values]
                        continue

                unique_values = set(row_values)
                cell_colour = self.get_cell_colour(row.cells[0])

                if len(unique_values) == 1:
                    value = list(unique_values)[0]
                    if value == "Ogólnomiejskie":
                        district = "OGOLNOMIEJSKI"
                        subdistrict = "OGOLNOMIEJSKI"
                        continue

                    if cell_colour.lower() == self.cell_colours["district"]:
                        district = value.title()
                        continue
                    elif cell_colour.lower() == self.cell_colours["size"]:
                        if "małe" in value.lower():
                            subdistrict = "small"
                        elif "duże" in value.lower():
                            subdistrict = "large"
                        continue

                # Construct a dictionary for this row, mapping keys to values
                row_data = dict(zip(keys, row_values))
                # print(row.cells[0]._tc.xml.w)

                selected = self.check_if_selected_project(row_data)
                row_data["selected"] = selected
                row_data["cost"] = utils.get_cost_from_text(row_data["cost"])
                row_data["votes"] = int(row_data["votes"].replace(" ", ""))
                row_data["name"] = row_data["name"].replace("\n", "")
                row_data["project_id"] = self.check_project_id(
                    row_data["project_id"])

                row_data = {k: row_data[k] for k in self.columns.values()}

                project_id = row_data["project_id"]
                if self.subdistricts:
                    if not self.projects_data_per_district.get(district):
                        self.projects_data_per_district[
                            district
                        ] = collections.defaultdict(list)
                        self.district_projects_mapping[
                            district
                        ] = collections.defaultdict(list)

                    self.projects_data_per_district[district][subdistrict].append(
                        row_data
                    )
                    self.district_projects_mapping[district][subdistrict].append(
                        project_id
                    )
                    self.project_district_mapping[project_id] = district
                    self.project_subdistrict_mapping[project_id] = subdistrict

    def check_if_selected_project(self, row_data):
        selected_text = row_data["selected"].replace("\n", "")
        if selected_text == "tak":
            return 1
        if (selected_text == "Projekt +1") or ("Asseco" in selected_text):
            # "sfinansowany przez Asseco Data Systems"
            # Additional funded project
            return 2
        return 0

    def initialize_mapping_dicts(self):
        self.projects_data_per_district = dict()
        self.district_projects_mapping = collections.defaultdict(list)
        self.project_district_mapping = dict()
        self.project_subdistrict_mapping = dict()

    def create_district_upper_mapping(self):
        self.district_upper_district_mapping = {
            "OGOLNOMIEJSKI": "Ogólnomiejskie"}
        for district in self.district_projects_mapping.keys():
            district_upper = utils.change_district_into_name(district)
            self.district_upper_district_mapping[district_upper] = district

    def create_project_item(self):
        project_id = None
        item = ProjectItem(project_id)
        name = None
        item.add_name(name)
        district = None
        self.logger.info(f"Processing Project: {project_id}")
        item.add_district(district.strip())
        item.project_url = None
        cost = None
        item.add_cost(cost)
        status = None
        item.add_selected(status)
        item.votes = None

        return item

    def start(self):
        docx_file = docx.Document(self.path_to_docx)
        self.get_data_from_docx_table(docx_file)
        self.create_district_upper_mapping()
        # self.create_district_name_mapping()
        objects = {
            "district_projects_mapping": self.district_projects_mapping,
            "projects_data_per_district": self.projects_data_per_district,
            "project_district_mapping": self.project_district_mapping,
            "project_subdistrict_mapping": self.project_subdistrict_mapping,
            "district_upper_district_mapping": self.district_upper_district_mapping,
        }
        self.save_mappings_as_jsons(objects)
