from copy import deepcopy
from datetime import datetime
from typing import Dict, List

import numpy as np
from werkzeug.datastructures import FileStorage

import src.utils.file_utils as file_utils
from src.app_manager.consts import STOPPING_CONDITIONS
from src.app_manager.problem import Problem
from src.app_manager.schedule_facade import SolutionSchedule
from src.app_manager.solution_analysis import SolutionAnalysis
from src.database.exceptions import ItemNotFoundInDB
from src.genetic_engine.ea_engine import EAEngine
from src.site_data_parser.data_classes import SiteData
from src.site_data_parser.site_data_parser import SiteDataParser
from src.utils.singleton import SingletonMeta
from src.database.database import db
from src.database.models import SiteData as DBSiteData
from src.database.models import Problem as DBProblem
from src.database.models import Solution as DBSolution

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
        site_data, site_data_dict = self.parser.parse_file(file)

        # update db
        with db.auto_commit():
            full_title = self._build_full_title(title)
            num_production_lines = len(site_data_dict["production_lines"])
            num_products = len(site_data_dict["products"])
            total_working_hours = site_data_dict["total_working_hours"]
            schedule_start_date = datetime.strptime(site_data_dict["schedule_start_date"], "%Y-%m-%d").date()
            individual_length = total_working_hours * num_products * num_production_lines
            db_site_data = DBSiteData(title=full_title, json_data=site_data_dict, num_products=num_products,
                                      num_production_lines=num_production_lines, schedule_start_date=schedule_start_date,
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
            file_name=f'site_data.json'
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

        return DBSiteData.query.all()

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
        self.problems[problem_id].engine.set_population_size(population_size)

        # update problem instance on db
        with db.auto_commit():
            db_problem, _ = self.get_problem_by_id(problem_id)

            tmp_data = deepcopy(db_problem.engine_data)
            tmp_data["population_size"] = population_size

            db_problem.engine_data = tmp_data

        return db_problem

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
        # fixme: BUG - when calling 'start run' immediately after app init, the app crashes over ORM session.
        # the hotfix would be to always call get_problem_by_id endpoint before start running.

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

    def set_stopping_condition(self, problem_id, cond_id, bound):
        problem: Problem = self.problems[problem_id]
        cond_str_id = STOPPING_CONDITIONS.get(cond_id)
        if cond_str_id == "TIME_STOPPING_CONDITION":
            # minutes to seconds
            bound = bound * 60
        problem.engine.set_stopping_condition(cond_str_id, bound)

        with db.auto_commit():
            db_problem, _ = self.get_problem_by_id(problem_id)

            tmp_data = deepcopy(db_problem.engine_data)
            tmp_data["stopping_conditions_configuration"][cond_str_id]["applied"] = True
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

    def get_saved_solutions_from_db(self):
        return [solution.as_dict() for solution in DBSolution.query.all()]

    def get_solution_from_db_by_id(self, solution_id) -> DBSolution:
        # get solution from db
        db_solution: DBSolution = DBSolution.query.filter_by(id=solution_id).first()
        if db_solution is None:
            raise ItemNotFoundInDB(f"item solution with id {solution_id} was not found in DB")
        return db_solution

    def save_solution_in_db(self, problem_id, title):
        _, problem = self.get_problem_by_id(problem_id)
        site_data = self.get_site_data_by_id(problem.site_data_id)
        current_solution = problem.get_current_best_solution()
        formatted_solution = SolutionSchedule.create_from_raw(current_solution, site_data)

        with db.auto_commit():
            db_solution = DBSolution(problem_id=problem_id, solution=formatted_solution.to_dict(), title=title,
                                     fitness=current_solution.fitness.values[0], time_modified=datetime.now(),
                                     raw_materials_usage=formatted_solution.raw_materials_usage,
                                     forecast_achieved=formatted_solution.forecast_achieved,
                                     product_line_utilization=formatted_solution.product_line_utilization)
            db.session.add(db_solution)

    def edit_saved_solution(self, solution_id: int, production_line: int, key: int, new_product_id: int,
                            new_datetime: List[str]) -> DBSolution:
        db_solution: DBSolution = self.get_solution_from_db_by_id(solution_id)
        site_data: DBSiteData = self.get_site_data_by_id(self.problems[db_solution.problem_id].site_data_id)

        new_product_name = None
        for product in site_data.json_data['products']:
            if product['id'] == new_product_id:
                new_product_name = product['name']
                break

        found_event = False
        with db.auto_commit():
            new_solution = deepcopy(db_solution.solution)
            raw_solution: np.ndarray = SolutionSchedule.convert_to_raw(new_solution['data'], site_data)
            SolutionSchedule.verify_conversion(raw_solution, new_solution, site_data)

            db_solution.fitness = self.problems[db_solution.problem_id].engine._calculate_fitness(raw_solution)

            new_solution['forecast_achieved'] = SolutionAnalysis.get_achieved_forecast(raw_solution, site_data)
            new_solution['raw_materials_usage'] = SolutionAnalysis.get_raw_materials_usage(raw_solution, site_data)
            new_solution['product_line_utilization'] = SolutionAnalysis.get_product_lines_utilization(raw_solution, site_data)

            for event in new_solution['data'][str(production_line)]:
                if event['key'] == key:
                    found_event = True
                    event['product_id'] = new_product_id
                    event['product_name'] = new_product_name
                    event['start_time'] = new_datetime[0]
                    event['end_time'] = new_datetime[1]
                    break

            if not found_event:
                raise ItemNotFoundInDB(f"in solution {solution_id}, production_line {production_line}, key {key} doesnt exist")

            db_solution.solution = new_solution

        return db_solution
