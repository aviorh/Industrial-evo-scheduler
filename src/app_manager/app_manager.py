import uuid
from typing import List
from itertools import count

from src.app_manager.problem import Problem
from src.site_data_parser.data_classes import SiteData
from src.utils.singleton import SingletonMeta


class AppManager(metaclass=SingletonMeta):
    """
    singleton class

    collection of problems
    collection of site-data
    collection of users

    """

    def __init__(self):
        self.problems_id_counter = 0

        self.problems: List[Problem] = []
        self.site_data_list: List[SiteData] = []
        # users: List[User] = []

    def add_problem(self, problem: Problem):
        self.problems.append(problem)
        self.problems_id_counter += 1

    def get_new_problem_id(self):
        return self.problems_id_counter

    def get_site_data_by_id(self, site_data_id: int):
        for site_data in self.site_data_list:
            if site_data.id == site_data_id:
                return site_data

        raise ValueError(f"site data {site_data_id} not found")

    def get_problem_by_id(self, problem_id: int) -> Problem:
        for problem in self.problems:
            if problem.id == problem_id:
                return problem

        raise ValueError(f"Problem {problem_id} not found")
