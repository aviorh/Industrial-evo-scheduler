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
        self.site_data_collection: Dict[int, SiteData] = dict()
        # users: List[User] = []

    # fixme: engine is not json serializable
    def add_problem(self, problem: Problem):
        self.problems[self.problem_counter] = problem
        self.problem_counter += 1
        return problem

    def create_problem(self, site_data_id):
        ea_engine = EAEngine(site_data=self.get_site_data_by_id(site_data_id))
        problem = Problem(id=self.problem_counter, site_data_id=site_data_id, engine=ea_engine)
        return self.add_problem(problem)

    # fixme: return 404 not found when there is keyError
    def get_site_data_by_id(self, site_data_id: int) -> DBSiteData:
        # fixme: to be removed when site-data in db is fully integrated
        # return self.site_data_collection.get(site_data_id)
        site_data: DBSiteData = DBSiteData.query.filter_by(id=site_data_id).first()
        if site_data is None:
            raise ItemNotFoundInDB(f"item site_data with id {site_data_id} was not found in DB")
        return site_data

    # fixme: return 404 not found when there is keyError
    def get_problem_by_id(self, problem_id: int):
        return self.problems.get(problem_id)

    def create_site_data(self, file: FileStorage):
        self.save_site_data_file(file)
        site_data, site_data_dict = self.parser.parse_file(file, self.site_data_counter)

        # fixme: to be removed when site-data in db is fully integrated
        self.site_data_collection[self.site_data_counter] = site_data
        self.site_data_counter += 1

        # update db
        with db.auto_commit():
            num_production_lines = len(site_data_dict["production_lines"])
            num_products = len(site_data_dict["products"])
            total_working_hours = len(site_data_dict["total_working_hours"])
            individual_length = total_working_hours * num_products * num_production_lines
            db_site_data = DBSiteData(data=site_data_dict, num_products=num_products,
                                      num_production_lines=num_production_lines,
                                      total_working_hours=total_working_hours, individual_length=individual_length)
            db.session.add(db_site_data)

        return site_data

    def save_site_data_file(self, file: FileStorage):
        file_utils.save_file(
            file=file,
            dir_path='site_data',
            file_name=f'site_data_{self.site_data_counter}.json'
        )

    def delete_problem(self, problem_id: int):
        del self.problems[problem_id]
        return self.problems

    # fixme: return apiError with status code 409 in case of a conflict
    def delete_site_data(self, site_data_id):
        relevant_problems = [problem for problem in self.problems.values() if problem.site_data_id == site_data_id]
        if len(relevant_problems) > 0:
            return "status code 409 - conflict. could not delete the data"
        else:
            # fixme: to be removed when site-data in db is fully integrated
            del self.site_data_collection[site_data_id]

            # update db
            with db.auto_commit():
                site_data = DBSiteData.query.filter_by(id=site_data_id).first()
                if site_data is None:
                    raise ItemNotFoundInDB(f"item site_data with id {site_data_id} was not found in DB")
                db.session.delete(site_data)

        return self.site_data_collection

    def add_mutation(self, problem_id, mutation_id, mutation_params):
        problem = self.get_problem_by_id(problem_id)
        problem.engine.add_mutation(mutation_id, mutation_params)
        return problem

    def set_crossover_method(self, problem_id, crossover_id, crossover_params):
        problem = self.get_problem_by_id(problem_id)
        problem.engine.set_crossover_method(crossover_id, crossover_params)
        return problem

    def set_population_size(self, problem_id, population_size):
        problem = self.get_problem_by_id(problem_id)
        problem.engine.set_population_size(population_size)
        return problem

    def set_selection_method(self, problem_id, selection_id, selection_params):
        problem = self.get_problem_by_id(problem_id)
        problem.engine.set_selection_method(selection_id, selection_params)
        return problem

    def start_running(self, problem_id):
        problem = self.get_problem_by_id(problem_id)
        problem.engine.start()

    def pause_problem(self, problem_id):
        problem = self.get_problem_by_id(problem_id)
        problem.engine.pause()

    def resume_problem(self, problem_id):
        problem = self.get_problem_by_id(problem_id)
        problem.engine.resume()

    def cleanup_problem(self, problem_id):
        problem = self.get_problem_by_id(problem_id)
        problem.perform_engine_cleanup()

    def set_stopping_condition(self, problem_id, cond_id, bound):
        problem = self.get_problem_by_id(problem_id)
        cond_str_id = STOPPING_CONDITIONS.get(cond_id)
        if cond_str_id == "TIME_STOPPING_CONDITION":
            # minutes to seconds
            bound = bound * 60
        problem.engine.set_stopping_condition(cond_str_id, bound)
        return cond_str_id

    def delete_stopping_condition(self, problem_id, cond_id):
        problem = self.get_problem_by_id(problem_id)
        cond_str_id = STOPPING_CONDITIONS.get(cond_id)
        problem.engine.delete_stopping_condition(cond_str_id)

    def get_progress(self, problem_id):
        problem = self.get_problem_by_id(problem_id)
        return problem.engine.stopping_conditions_configuration
