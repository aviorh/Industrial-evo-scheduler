from copy import deepcopy
from datetime import datetime
from typing import Dict

from werkzeug.datastructures import FileStorage

import src.utils.file_utils as file_utils
from src.app_manager.consts import STOPPING_CONDITIONS
from src.app_manager.problem import Problem
from src.database.exceptions import ItemNotFoundInDB
from src.genetic_engine.ea_engine import EAEngine
from src.site_data_parser.data_classes import SiteData
from src.site_data_parser.site_data_parser import SiteDataParser
from src.utils.singleton import SingletonMeta
from src.database.database import db
from src.database.models import SiteData as DBSiteData
from src.database.models import Problem as DBProblem

STATUS_PAUSED = 'paused'
STATUS_IDLE = 'idle'
STATUS_RUNNING = 'running'


class AppManager(metaclass=SingletonMeta):
    """
    singleton class

    collection of problems
    collection of site-data
    collection of users

    """
    site_data_counter = 0  # used for creating ids for SiteData
    problem_counter = 0  # used for creating ids for Problem

    def __init__(self):
        self.parser = SiteDataParser()
        self.problems: Dict[int, Problem] = dict()

        self._load_problems_from_db()

    def _load_problems_from_db(self):
        if db is not None:
            db_problems = DBProblem.query.all()
            for db_problem in db_problems:
                with db.auto_commit():
                    db_problem.status = STATUS_IDLE
                self._create_problem_from_db(db_problem)

    def _create_problem_from_db(self, db_problem: DBProblem):
        ea_engine = EAEngine(site_data=self.get_site_data_by_id(db_problem.site_data_id))
        problem = Problem(id=db_problem.id, site_data_id=db_problem.site_data_id, engine=ea_engine, title=db_problem.title)
        self.problems[problem.id] = problem

    def create_problem(self, site_data_id, title, is_full_title=False):
        full_title = title if is_full_title else self._build_full_title(title)

        with db.auto_commit():
            db_problem = DBProblem(title=full_title, site_data_id=site_data_id)
            db.session.add(db_problem)

        # init engine in both db and memory
        ea_engine = EAEngine(site_data=self.get_site_data_by_id(site_data_id))
        with db.auto_commit():
            db_problem.engine_data = ea_engine.to_dict()

        problem = Problem(id=db_problem.id, site_data_id=site_data_id, engine=ea_engine, title=full_title)
        self.problems[problem.id] = problem

        return problem

    # fixme: return 404 not found when there is keyError
    def get_site_data_by_id(self, site_data_id: int) -> DBSiteData:
        site_data: DBSiteData = DBSiteData.query.filter_by(id=site_data_id).first()
        if site_data is None:
            raise ItemNotFoundInDB(f"item site_data with id {site_data_id} was not found in DB")
        return site_data

    # fixme: return 404 not found when there is keyError
    def get_problem_by_id(self, problem_id: int) -> (DBProblem, Problem):
        # get problem from db
        db_problem: DBProblem = DBProblem.query.filter_by(id=problem_id).first()
        if db_problem is None:
            raise ItemNotFoundInDB(f"item problem with id {problem_id} was not found in DB")
        problem: Problem = self.problems[problem_id]
        return db_problem, problem

    def create_site_data(self, file: FileStorage, title: str):
        self.save_site_data_file(file)
        site_data, site_data_dict = self.parser.parse_file(file, self.site_data_counter)

        # update db
        with db.auto_commit():
            full_title = self._build_full_title(title)
            num_production_lines = len(site_data_dict["production_lines"])
            num_products = len(site_data_dict["products"])
            total_working_hours = site_data_dict["total_working_hours"]
            individual_length = total_working_hours * num_products * num_production_lines
            db_site_data = DBSiteData(title=full_title, json_data=site_data_dict, num_products=num_products,
                                      num_production_lines=num_production_lines,
                                      total_working_hours=total_working_hours, individual_length=individual_length)
            db.session.add(db_site_data)

        return site_data

    def _build_full_title(self, title):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M")
        return f"{title} - {dt_string}"

    def save_site_data_file(self, file: FileStorage):
        file_utils.save_file(
            file=file,
            dir_path='site_data',
            file_name=f'site_data_{self.site_data_counter}.json'
        )

    def delete_problem(self, problem_id: int):
        with db.auto_commit():
            db_problem, _ = self.get_problem_by_id(problem_id)
            db.session.delete(db_problem)

        del self.problems[problem_id]
        return [problem.to_dict_format() for problem in self.problems.values()]

    # fixme: return apiError with status code 409 in case of a conflict
    def delete_site_data(self, site_data_id):
        relevant_problems = [problem for problem in self.problems.values() if problem.site_data_id == site_data_id]
        if len(relevant_problems) > 0:
            return "status code 409 - conflict. could not delete the data"
        else:
            with db.auto_commit():
                site_data: DBSiteData = self.get_site_data_by_id(site_data_id)
                if site_data is None:
                    raise ItemNotFoundInDB(f"item site_data with id {site_data_id} was not found in DB")
                db.session.delete(site_data)

        return [site_data.as_dict() for site_data in DBSiteData.query.all()]

    def add_mutation(self, problem_id, mutation_id, mutation_params):
        db_problem, problem = self.get_problem_by_id(problem_id)
        problem.engine.add_mutation(mutation_id, mutation_params)

        with db.auto_commit():
            tmp_data = deepcopy(db_problem.engine_data)
            tmp_data["mutations"][0] = {"mutation_id": mutation_id, "params": mutation_params}

            db_problem.engine_data = tmp_data

        return problem

    def set_population_size(self, problem_id, population_size):
        # update problem instance in memory
        db_problem, problem = self.get_problem_by_id(problem_id)
        problem.engine.set_population_size(population_size)

        # update problem instance on db
        with db.auto_commit():
            tmp_data = deepcopy(db_problem.engine_data)
            tmp_data["population_size"] = population_size

            db_problem.engine_data = tmp_data

        return problem

    def set_crossover_method(self, problem_id, crossover_id, crossover_params):
        problem: Problem = self.problems[problem_id]
        problem.engine.set_crossover_method(crossover_id, crossover_params)

        with db.auto_commit():
            db_problem, _ = self.get_problem_by_id(problem_id)

            tmp_data = deepcopy(db_problem.engine_data)
            tmp_data["crossover_method"]["method_id"] = crossover_id
            tmp_data["crossover_method"]["params"] = crossover_params

            db_problem.engine_data = tmp_data
        return problem

    def set_selection_method(self, problem_id, selection_id, selection_params):
        problem: Problem = self.problems[problem_id]
        problem.engine.set_selection_method(selection_id, selection_params)

        with db.auto_commit():
            db_problem, _ = self.get_problem_by_id(problem_id)

            tmp_data = deepcopy(db_problem.engine_data)
            tmp_data["selection_method"]["method_id"] = selection_id
            tmp_data["selection_method"]["params"] = selection_params

            db_problem.engine_data = tmp_data

        return problem

    def start_running(self, problem_id):
        db_problem, problem = self.get_problem_by_id(problem_id)
        problem.engine.start()

        with db.auto_commit():
            db_problem.status = STATUS_RUNNING
            problem.status = STATUS_RUNNING

    def pause_problem(self, problem_id):
        db_problem, problem = self.get_problem_by_id(problem_id)
        problem.engine.pause()

        with db.auto_commit():
            db_problem.status = STATUS_PAUSED
            problem.status = STATUS_PAUSED

    def resume_problem(self, problem_id):
        db_problem, problem = self.get_problem_by_id(problem_id)
        problem.engine.resume()

        with db.auto_commit():
            db_problem.status = STATUS_RUNNING
            problem.status = STATUS_RUNNING

    def cleanup_problem(self, problem_id):
        db_problem, problem = self.get_problem_by_id(problem_id)
        problem.perform_engine_cleanup()

        with db.auto_commit():
            db_problem.engine_data = problem.engine.to_dict()
            db_problem.status = STATUS_IDLE
            problem.status = STATUS_IDLE

    def set_stopping_condition(self, problem_id, cond_id, bound, applied):
        problem: Problem = self.problems[problem_id]
        cond_str_id = STOPPING_CONDITIONS.get(cond_id)
        if cond_str_id == "TIME_STOPPING_CONDITION":
            # minutes to seconds
            bound = bound * 60
        problem.engine.set_stopping_condition(cond_str_id, bound, applied)

        with db.auto_commit():
            db_problem, _ = self.get_problem_by_id(problem_id)

            tmp_data = deepcopy(db_problem.engine_data)
            tmp_data["stopping_conditions_configuration"][cond_str_id]["applied"] = applied
            tmp_data["stopping_conditions_configuration"][cond_str_id]["bound"] = bound

            db_problem.engine_data = tmp_data

        return cond_str_id

    def delete_stopping_condition(self, problem_id, cond_id):
        db_problem, problem = self.get_problem_by_id(problem_id)
        cond_str_id = STOPPING_CONDITIONS.get(cond_id)
        problem.engine.delete_stopping_condition(cond_str_id)

        with db.auto_commit():
            tmp_data = deepcopy(db_problem.engine_data)
            tmp_data["stopping_conditions_configuration"][cond_str_id]["applied"] = False
            tmp_data["stopping_conditions_configuration"][cond_str_id]["bound"] = 0

            db_problem.engine_data = tmp_data

    def get_progress(self, problem_id):
        _, problem = self.get_problem_by_id(problem_id)
        return problem.engine.stopping_conditions_configuration

    def get_sites_data(self):
        return [site_data.as_dict() for site_data in DBSiteData.query.all()]

