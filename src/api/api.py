from src.app_manager.app_manager import AppManager
from src.app_manager.problem import Problem
from src.genetic_engine.ea_engine import EAEngine


def trigger_sched():
    return 'success'


def add_problem(site_data_id: int):
    app_manager = AppManager()

    ea_engine = EAEngine(site_data=app_manager.get_site_data_by_id(site_data_id))
    problem = Problem(id=app_manager.get_new_problem_id(), siteDataId=site_data_id, engine=ea_engine)

    app_manager.add_problem(problem)


def get_problem_by_id(problem_id: int):
    app_manager = AppManager()
    problem = app_manager.get_problem_by_id(problem_id)

    return problem

