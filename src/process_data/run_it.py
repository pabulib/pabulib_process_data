import helpers.utilities as utils
from process_data.create_meta_section import CreateMetaSections
from process_data.create_projects_section import CreateProjectsSections
from process_data.create_votes_section import CreateVotesSections
from process_data.get_projects_excel import GetProjects
from process_data.get_votes_excel import GetVotesExcel

unusual_units = ["mechanical_turk", "stanford"]


def run_it(year, unit):

    unit_package = utils.remove_accents_from_str(unit)
    packages = f"process_data.cities.{unit_package.lower()}"

    all_data = getattr(
        __import__(f"{packages}.settings", fromlist=["all_data"]), "all_data"
    )

    data = all_data[year]

    preprocessing = data.get("preprocess")

    if preprocessing:
        Preprocess = getattr(
            __import__(f"{packages}.preprocess", fromlist=["Preprocess"]), "Preprocess"
        )
        pp = Preprocess(
            **data["base_data"],
            **{"preprocess": data.get("preprocess")},
        )
        pp.start()

    if unit in unusual_units:
        ProcessData = getattr(
            __import__(f"{packages}.process_data", fromlist=["ProcessData"]),
            "ProcessData",
        )
        pd = ProcessData(**data["base_data"], **{"metadata": data["metadata"]})
        pd.start()
        return

    budgets = getattr(
        __import__(f"{packages}.budgets", fromlist=["budgets"]), "budgets"
    )

    logger = utils.create_logger()

    # GET PROJECTS
    logger.info(f"{unit}, year: {year}, getting projects...")
    try:
        gp = getattr(
            __import__(f"{packages}.get_projects", fromlist=["GetProjects"]),
            "GetProjects",
        )
    except ModuleNotFoundError:
        gp = GetProjects
    sp = gp(**data["base_data"], **data["get_projects"])
    sp.start()

    # GET VOTES FROM EXCEL FILE
    # logger.info('Getting votes from excel file...')
    gv = GetVotesExcel(**data["base_data"], **data["get_votes"])
    gv.get_votes()

    # CREATE PB FILES AND SAVE PROJECTS SECTIONS
    logger.info("Creating PB files and save with PROJECTS sections")
    cps = CreateProjectsSections(**data["base_data"], **data["projects_data"])
    cps.create_projects_sections()

    # ADD VOTES SECTIONS TO PB FILES
    logger.info("Adding VOTES sections...")
    cvs = CreateVotesSections(**data["base_data"], **data["votes_data"])
    cvs.create_votes_sections()

    # # ADD META SECTIONS TO PB FILES
    logger.info("Adding METADATA sections...")
    cms = CreateMetaSections(
        **data["base_data"],
        **{"budgets": budgets[year]},
        **{"metadata": data["metadata"]},
    )
    cms.add_metadata()
