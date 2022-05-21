from dataclasses import dataclass, field, asdict
from datetime import datetime


import matplotlib.pyplot as plt
import seaborn as sns

from src.genetic_engine.ea_engine import EAEngine
from src.utils.file_utils import ROOT
from flask import send_file


def _get_datetime_str() -> str:
    current_datetime = datetime.now()
    return current_datetime.strftime("%d/%m/%Y %H:%M")


@dataclass
class Problem:
    """
    id
    date from & to
    description
    site_data_list (taken from collection)
    engine (new instance per problem)
    timetable in response format (json?)
    
    """
    id: int
    site_data_id: int
    engine: EAEngine
    description: str = ''
    creation_time: str = field(default_factory=_get_datetime_str)
    schedule: str = None  # json? dict?

    def to_dict_format(self):
        return {
            "id": self.id,
            "site_data_id": self.site_data_id,
            "engine": self.engine.to_dict(),
            "description": self.description,
            "creation_time": self.creation_time,
            "schedule": None
        }

    def get_current_best_solution(self):
        # here we only read from HOF, so no need to worry about thread-safety
        current_best_solution = self.engine.hall_of_fame.items[0]
        return current_best_solution.tolist()

    def get_fitness_logbook(self):
        # here we only read from logbook, so no need to worry about thread-safety
        return self.engine.logbook

    def get_fitness_graph_as_img(self):
        # extract statistics:
        min_fitness_values, mean_fitness_values = self.engine.logbook.select("min_fitness", "avg_fitness")

        # plot statistics:
        sns.set_style("whitegrid")
        plt.plot(min_fitness_values, color='red')
        plt.plot(mean_fitness_values, color='green')
        plt.xlabel('Generation')
        plt.ylabel('Min / Average Fitness')
        plt.title('Min and Average fitness over Generations')

        # save graph to file in backend local_database
        graph_filepath = f"{ROOT}/graph{self.id}.png"
        plt.savefig(graph_filepath)

        return send_file(graph_filepath)