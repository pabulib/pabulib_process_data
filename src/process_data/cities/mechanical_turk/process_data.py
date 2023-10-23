from copy import deepcopy
from dataclasses import dataclass

import helpers.utilities as utils
from process_data.base_config import BaseConfig

election_type_mapping = {
    "Knapsack": "approval",
    "Threshold": "approval",
    "k_approval": "approval",
    "Ranking_value": "ordinal",
    "Ranking_value_money": "ordinal",
    "Utilities": "cumulative"
}


@dataclass
class ProcessData(BaseConfig):
    excel_filename: str
    metadata: dict

    def __post_init__(self):
        self.prepare_excel()
        return super().__post_init__()

    def get_sheet_and_col_names(self, name):
        sheet = self.workbook.sheet_by_name(name)
        data = [sheet.row_values(i) for i in range(sheet.nrows)]
        data = data[1:]
        col_names = utils.get_col_names_indexes(sheet)
        return data, col_names

    def prepare_excel(self):
        excel_path = utils.get_path_to_file_by_unit(
            self.excel_filename, self.unit,
        )
        self.workbook = utils.get_workbook(excel_path)

    def get_experiments(self):
        exp_data, exp_col_names = self.get_sheet_and_col_names(
            'Valid_experiments')

        self.elections = {}
        self.experiments = {}
        # self.voting_methods = set()
        self.participant_exp_mapping = {}

        for row_data in exp_data:
            exp_id = int(row_data[exp_col_names["EXP_ID"]])
            participant_id = row_data[exp_col_names["PARTICIPANT_ID"]].strip()
            voting_method = row_data[exp_col_names["INPUT_FORMAT"]]
            # self.voting_methods.add(voting_method)

            election_id = int(row_data[exp_col_names["ELECTION_NUM"]])
            instance_id = f'{voting_method}_{election_id}'

            self.elections.setdefault(instance_id, set()).add(exp_id)

            self.experiments[exp_id] = {"voting_method": voting_method}
            self.participant_exp_mapping[participant_id] = exp_id

    def get_participants(self):
        part_data, part_col_names = self.get_sheet_and_col_names(
            'Participants')
        for row_data in part_data:

            participant_id = row_data[part_col_names["PARTICIPANT_ID"]].strip()
            age = int(row_data[part_col_names["AGE"]])
            education = row_data[part_col_names["EDUCATION"]]
            sex = row_data[part_col_names["GENDER"]][0]

            try:
                exp_id = int(self.participant_exp_mapping[participant_id])
            except KeyError:
                continue

            try:
                self.experiments[exp_id]["age"] = age
                self.experiments[exp_id]["education"] = education
                self.experiments[exp_id]["sex"] = sex
            except KeyError:
                self.logger.error(
                    f'There is no exp_id: {exp_id}, "{participant_id}"')

    def get_votes(self):
        votes_data, votes_col_names = self.get_sheet_and_col_names(
            'Experiment items')

        votes = {}
        votes_removed = {}
        vote_list = []
        before_list = ['x'] * 20
        after_list = ['x'] * 20

        for idx, row_data in enumerate(votes_data):

            exp_id = int(row_data[votes_col_names["EXP_ID"]])
            project_id = int(row_data[votes_col_names["ITEM_ID"]])
            if row_data[votes_col_names["RANK_BEFORE"]]:

                rank_before = int(row_data[votes_col_names["RANK_BEFORE"]])
                before_list[rank_before] = project_id
                rank_after = int(row_data[votes_col_names["RANK_AFTER"]])
                after_list[rank_after] = project_id
            else:
                vote = int(row_data[votes_col_names["VALUE"]])
                if vote != 0:
                    vote_dict = {"project_id": project_id, "points": vote}
                    vote_list.append(vote_dict)

            if (len(votes_data) == idx + 1) or (int(votes_data[idx+1][votes_col_names["EXP_ID"]]) != exp_id):

                if row_data[votes_col_names["RANK_BEFORE"]]:
                    vote_list = [before_list, after_list]
                    if 'x' in vote_list[0]:
                        if vote_list[0][10] == 'x':
                            vote_list[0] = vote_list[0][:10]
                            vote_list[1] = vote_list[1][:10]
                            if 'x' in vote_list[0]:
                                votes_removed[exp_id] = vote_list
                                vote_list = []
                                continue

                    before_list = ['x'] * 20
                    after_list = ['x'] * 20
                votes[exp_id] = vote_list

                vote_list = []

        self.logger.info(
            f'Removed votes! Voters IDs: {list(votes_removed.keys())}')
        return votes

    def check_if_exceeded_points(self, points, voter):
        # TODO set the threshold
        NORMALIZE_THRESHOLD = 104

        if sum(points) > 100:
            if sum(points) < NORMALIZE_THRESHOLD:

                quotients = utils.largest_remainder_method(points)
                self.logger.info(
                    f'\nSum of points higher than 100 but less than '
                    f'{NORMALIZE_THRESHOLD}! Normalizing to 100...\n'
                    f'before: {points}\nafter: {quotients}')
                if sum(quotients) == 100:
                    return quotients
                else:
                    raise RuntimeError("Largest remainder method doesn't work")
            else:
                self.logger.info(
                    f'Voter {voter} was removed! Sum of points: {sum(points)}')
                return
        return points

    def aggregate_votes(self, votes):

        self.aggregated_votes = {}

        for voter, vote in votes.items():
            if isinstance(vote[0], dict):
                projects_agg = []
                points_agg = []
                for vote_dict in vote:
                    projects_agg.append(vote_dict['project_id'])
                    points_agg.append(vote_dict['points'])
                    if set(points_agg) == {1}:
                        self.aggregated_votes[voter] = projects_agg
                    else:
                        zipped = {x: y for x, y in zip(
                            projects_agg, points_agg)}
                        sorted_by_points = {k: v for k, v in sorted(
                            zipped.items(), key=lambda item: item[1], reverse=True)}
                        projects = list(sorted_by_points.keys())
                        points = list(sorted_by_points.values())
                        points = self.check_if_exceeded_points(points, voter)
                        if not points:
                            continue

                        self.aggregated_votes[voter] = {
                            "projects": projects, "points": points}
            else:
                self.aggregated_votes[voter] = vote

    def get_projects(self):
        projects_data, projects_col_names = self.get_sheet_and_col_names(
            'Items')

        self.all_projects = {}

        for row_data in projects_data:

            project_id = int(row_data[projects_col_names["ITEM_ID"]])
            name = row_data[projects_col_names["ITEM_NAME"]]
            cost = row_data[projects_col_names["VALUE"]]
            description = row_data[projects_col_names["DESCRIPTION"]]
            category = row_data[projects_col_names["GROUP_NAME"]]
            singular = row_data[projects_col_names["SINGULAR"]]  # ??

            self.all_projects[project_id] = {
                "name": name,
                "cost": cost,
                "description": description,
                "category": category,
                "singular": singular
            }

    def get_election_project_mapping(self):

        e_p_data, e_p_col_names = self.get_sheet_and_col_names('Elections')

        self.election_project_mapping = {}

        for row_data in e_p_data:
            election = int(row_data[e_p_col_names["Election"]])
            project_id = int(row_data[e_p_col_names["ITEM_ID"]])
            self.election_project_mapping.setdefault(
                election, set()).add(project_id)

    def add_votes_section(self, csv_file, points):
        fields = ["voter_id", "age", "sex", "education", "vote"]
        if points:
            fields.append("points")
        csv_file.writerow(["VOTES"])
        csv_file.writerow(fields)

    def add_projects_section(self, csv_file, points, save_votes=True):
        fields = ["project_id", "name", "cost",
                  "description", "category", "votes"]
        if not save_votes:
            fields.pop()
        if points:
            fields.append("score")
        csv_file.writerow(["PROJECTS"])
        csv_file.writerow(fields)

    def get_voter_info(self, voter):
        sex = self.experiments[voter].get("sex")
        age = self.experiments[voter].get("age")
        education = self.experiments[voter].get("education")
        voter_row = [voter, age, sex, education]
        return voter_row

    def get_cumulative_votes(self, votes):
        projects = [str(project) for project in votes['projects']]
        projects = ",".join(projects)
        points = [str(project) for project in votes['points']]
        points = ",".join(points)

        for project_id, points_ in zip(votes['projects'], votes['points']):
            self.counted_votes["votes"][project_id] = self.counted_votes["votes"].get(
                project_id, 0) + 1
            self.counted_votes["points"][project_id] = self.counted_votes["points"].get(
                project_id, 0) + points_
        return projects, points

    def get_ordinal_votes(self, vote):
        for idx, project_id in enumerate(reversed(vote)):
            points = idx + 1
            self.counted_votes["votes"][project_id] = self.counted_votes["votes"].get(
                project_id, 0) + 1
            self.counted_votes["points"][project_id] = self.counted_votes["points"].get(
                project_id, 0) + points
        vote = [str(project) for project in vote]
        vote = ",".join(vote)
        return vote

    def get_approval_votes(self, votes):
        for project_id in votes:
            self.counted_votes["votes"][project_id] = self.counted_votes["votes"].get(
                project_id, 0) + 1
        votes = [str(project) for project in votes]
        vote = ",".join(votes)
        return vote

    def handle_election(self, election, voters):
        self.logger.info(f"Processing election: {election}...")

        e_type, e_number = election.rsplit('_', 1)
        election_type = election_type_mapping[e_type]

        self.counted_votes = {}
        self.counted_votes["votes"] = {}

        save_points = False
        save_votes = True
        if election_type in ('cumulative', 'ordinal'):
            save_points = True
            self.counted_votes["points"] = {}

            if election_type == "ordinal":
                save_votes = False

        # create file
        file_, csv_file = utils.create_csv_file(election)

        # get votes
        vote_rows = self.get_vote_rows(voters, election_type)

        # order projects by score / votes
        self.sort_projects(e_number, save_points)

        # create projects section
        self.add_projects_section(csv_file, save_points, save_votes)
        projects_rows = self.get_projects_rows(election_type, save_points)
        for project_row in projects_rows:
            csv_file.writerow(project_row)

        if election_type == 'ordinal':
            save_points = False

        # create votes section
        self.add_votes_section(csv_file, save_points)
        for row in vote_rows:
            csv_file.writerow(row)

        file_.close()

        self.add_metadata(election, election_type)

    def add_metadata(self, election, election_type):
        # add meta section
        path_to_file = utils.get_path_to_file(election)
        num_projects, num_votes = utils.count_projects_and_votes(path_to_file)
        temp_meta = deepcopy(self.metadata)
        description = temp_meta.pop("description")

        metadata = (
            "META\n"
            "key;value\n"
            f"description;{description}\n"
            f"country;{self.country}\n"
            f"unit;{self.unit}\n"
            f"instance;{self.instance}\n"
            f"num_projects;{num_projects}\n"
            f"num_votes;{num_votes}\n"
            f"vote_type;{election_type}\n"
        )
        if election_type == "approval":
            if election.startswith('Knapsack'):
                min_length = '1'
                max_length = '11'
            elif election.startswith('k_approval'):
                min_length = '2'
                max_length = '5'
            elif election.startswith('Threshold'):
                min_length = '1'
                max_length = '14'

            metadata += f"min_length;{min_length}\n"
            metadata += f"max_length;{max_length}\n"
        elif election_type == "ordinal":
            if election.endswith(('_7', '_8')):
                # 'Ranking_value_7', 'Ranking_value_8'
                # 'Ranking_value_money_7', 'Ranking_value_money_8'
                min_length = '20'
                max_length = '20'
            else:
                min_length = '10'
                max_length = '10'

            metadata += f"min_length;{min_length}\n"
            metadata += f"max_length;{max_length}\n"
        elif election_type == "cumulative":
            metadata += "max_sum_points;100\n"
            metadata += "min_sum_points;100\n"
            # max_sum_cost ?

            # max_sum_cost ??
            # "min_length": "1",
            # "max_length": "3",
        for key, value in temp_meta.items():
            metadata += f"{key};{value}\n"

        utils.prepend_line_at_the_beggining_of_file(metadata, path_to_file)

    def get_vote_rows(self, voters, election_type):
        vote_rows = []
        for voter in voters:
            voter_row = self.get_voter_info(voter)
            votes = self.aggregated_votes[voter]

            if election_type == "cumulative":
                # cumulative (points)
                projects, points = self.get_cumulative_votes(votes)
                vote_rows.append(voter_row + [projects, points])

            elif election_type == "ordinal":
                # ordinal (ranks)
                vote = self.aggregated_votes[voter][1]
                vote = self.get_ordinal_votes(vote)
                vote_rows.append(voter_row + [vote])

            elif election_type == "approval":
                # approval (no points)
                vote = self.get_approval_votes(votes)
                vote_rows.append(voter_row + [vote])
            else:
                self.logger.error(
                    f'Election type not recognized: {election_type}')
        return vote_rows

    def sort_projects(self, e_number, save_points):
        election_projects = self.election_project_mapping[int(e_number)]
        if save_points:
            projects_list = [(self.counted_votes["points"]
                             [project_id], project_id) for project_id in election_projects]
        else:
            projects_list = [(self.counted_votes["votes"]
                             [project_id], project_id) for project_id in election_projects]
        self.projects_sorted = sorted(
            projects_list, key=lambda x: x[1], reverse=True)

    def get_projects_rows(self, election_type, save_points):
        for project_data in self.projects_sorted:
            project_id = project_data[1]
            name = self.all_projects[project_id]["name"]
            description = self.all_projects[project_id]["description"]
            cost = int(self.all_projects[project_id]["cost"])
            category = self.all_projects[project_id]["category"]
            votes = self.counted_votes["votes"][project_id]
            row = [project_id, name, cost, description, category, votes]
            if election_type == 'ordinal':
                row.pop()
            if save_points:
                score = self.counted_votes["points"][project_id]
                row.append(score)
            yield row

    def start(self):
        self.get_experiments()
        self.get_participants()
        votes = self.get_votes()
        self.aggregate_votes(votes)
        self.get_projects()
        self.get_election_project_mapping()

        for election, voters in self.elections.items():
            self.handle_election(election, voters)
