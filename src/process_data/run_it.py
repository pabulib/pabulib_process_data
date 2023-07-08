import helpers.utilities as utils

from process_data.create_meta_section import CreateMetaSections
from process_data.create_projects_section import CreateProjectsSections
from process_data.create_votes_section import CreateVotesSections
from process_data.get_votes_excel import GetVotesExcel


def run_it(year, unit, scrape_data=False, get_pdf_data=False):
    unit_package = utils.remove_accents_from_str(unit)
    packages = f'process_data.cities.{unit_package.lower()}'
    budgets = getattr(__import__(
        f'{packages}.budgets', fromlist=["budgets"]), "budgets")
    all_data = getattr(__import__(
        f'{packages}.settings', fromlist=["all_data"]), "all_data")

    data = all_data[year]
    logger = utils.create_logger()

    # SCRAPE PROJECTS FROM WEBPAGE
    if scrape_data:
        json_files = utils.check_if_json_files_in_output(
            'Poland', unit, year, logger)
        if json_files:
            logger.info(f'{unit}, year: {year}, skipping scraping because'
                        ' of JSON files in output directory')
        else:
            logger.info(f'{unit}, year: {year}, scraping web data...')
            GetProjects = getattr(__import__(f'{packages}.get_projects', fromlist=[
                "GetProjects"]), "GetProjects")
            sp = GetProjects(**data["base_data"], **data["get_projects"])
            sp.start()
    else:
        logger.info(f'{unit}, year: {year}, scraping web data skipped!')

    # GET VOTES FROM EXCEL FILE
    # logger.info('Getting votes from excel file...')
    gv = GetVotesExcel(**data["base_data"], **data["excel_data"])
    gv.get_votes()

    # CREATE PB FILES AND SAVE PROJECTS SECTIONS
    logger.info('Creating PB files and save with PROJECTS sections')
    cps = CreateProjectsSections(**data["base_data"], **data["projects_data"])
    cps.create_projects_sections()

    # ADD VOTES SECTIONS TO PB FILES
    logger.info('Adding VOTES sections...')
    cvs = CreateVotesSections(**data["base_data"], **data["votes_data"])
    cvs.create_votes_sections()

    # # ADD META SECTIONS TO PB FILES
    logger.info('Adding METADATA sections...')
    cms = CreateMetaSections(
        **data["base_data"],
        **{"budgets": budgets[year]},
        **{"metadata": data["metadata"]})
    cms.add_metadata()