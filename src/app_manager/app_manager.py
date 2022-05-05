import os
from typing import List
from itertools import count

from werkzeug.datastructures import FileStorage

from src.app_manager.problem import Problem
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

    # static variable, uses for creating ids for SiteData
    site_data_counter = 0

    def __init__(self):
        self.problem_ids = count(0)
        self.site_data_ids = count(0)
        self.user_ids = count(0)
        self.parser = SiteDataParser()

        self.problems: List[Problem] = []
        self.site_data_list: List[SiteData] = []
        # users: List[User] = []

    def add_problem(self, problem: Problem):
        self.problems.append(problem)
        self.problem_ids = next(self.problem_ids)

    def get_new_problem_id(self):
        return self.problem_ids

    def get_site_data_by_id(self, site_data_id: int):
        for site_data in self.site_data_list:
            if site_data.id == site_data_id:
                return site_data

        raise ValueError(f"site data {site_data_id} not found")

    def get_problem_by_id(self, problem_id: int):
        for problem in self.problems:
            if problem.id == problem_id:
                return problem

        raise ValueError(f"Problem {problem_id} not found")

    def create_site_data(self, file: FileStorage):
        self.save_site_data_file(file)
        site_data = self.parser.parse_file(file, self.site_data_counter)
        self.site_data_counter += 1
        self.site_data_list.append(site_data)
        return site_data

    def save_site_data_file(self, file: FileStorage):
        file_utils.save_file(
            file=file,
            dir_path='site_data',
            file_name=f'site_data_{self.site_data_counter}.json'
        )

