import os
from typing import List, Dict
from itertools import count

from werkzeug.datastructures import FileStorage

from src.app_manager.problem import Problem
from src.genetic_engine.ea_engine import EAEngine
from src.site_data_parser.data_classes import SiteData
from src.site_data_parser.site_data_parser import SiteDataParser
from src.utils.singleton import SingletonMeta
import src.utils.file_utils as file_utils


class AppManager(metaclass=SingletonMeta):
    """
    singleton class

    collection of problems
    collection of site-data
    collection of users

    """

    # static variable, used for creating ids for SiteData
    site_data_counter = 0

    #static variable, used for creating ids for Problem
    problem_counter = 0

    def __init__(self):
        self.problem_ids = count(0)
        self.site_data_ids = count(0)
        self.user_ids = count(0)
        self.parser = SiteDataParser()

        self.problems: Dict[int, Problem] = dict()
        self.site_data_collection: Dict[int, SiteData] = dict()
        # users: List[User] = []

    # fixme: engine is not json serializable
    def add_problem(self, problem: Problem):
        self.problems[self.problem_counter] = problem
        self.problem_counter += 1
        return problem

    def get_new_problem_id(self):
        return self.problem_ids

    def create_problem(self, site_data_id):

        ea_engine = EAEngine(site_data=self.get_site_data_by_id(site_data_id))
        problem = Problem(id=self.get_new_problem_id(), siteDataId=site_data_id, engine=ea_engine)

        return self.add_problem(problem)

    # fixme: return 404 not found when there is keyError
    def get_site_data_by_id(self, site_data_id: int):
        return self.site_data_collection.get(site_data_id)

    # fixme: return 404 not found when there is keyError
    def get_problem_by_id(self, problem_id: int):
        return self.problems.get(problem_id)

    def create_site_data(self, file: FileStorage):
        self.save_site_data_file(file)
        site_data = self.parser.parse_file(file, self.site_data_counter)
        self.site_data_collection[self.site_data_counter] = site_data
        self.site_data_counter += 1
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
            del self.site_data_collection[site_data_id]
        return self.site_data_collection
