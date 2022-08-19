import matplotlib
matplotlib.use("Agg")

import os.path
from dataclasses import dataclass, field
from datetime import datetime

import matplotlib.pyplot as plt
import seaborn as sns
from flask import send_file

from src.genetic_engine.ea_engine import EAEngine
from src.utils.file_utils import ROOT


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
    title: str
    creation_time: str = field(default_factory=_get_datetime_str)
    status: str = 'idle'  # idle/paused/running
    schedule: str = None  # json? dict?

    def to_dict_format(self):
        return {
            "id": self.id,
            "site_data_id": self.site_data_id,
            "engine": self.engine.to_dict(),
            "title": self.title,
            "creation_time": self.creation_time,
            "status": self.status,
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
        figure = plt.figure()
        figure.clear()
        ax = figure.add_subplot(1, 1, 1, title='Min and Average fitness over Generations',
                                xlabel='Generation', ylabel='Min / Average Fitness')
        ax.plot(min_fitness_values, color='red')
        ax.plot(mean_fitness_values, color='green')

        # save graph to file in backend local_database
        graph_filepath = os.path.join(ROOT, f"graph{self.id}.png")
        if os.path.isfile(graph_filepath):
            os.remove(graph_filepath)

        figure.savefig(graph_filepath)
        return send_file(graph_filepath)

    def perform_engine_cleanup(self):
        old_engine = self.engine
        old_engine.notify_run_termination()
        old_engine.join()

        new_engine = self.engine.new_engine_from_existing()
        self.engine = new_engine

        del old_engine

