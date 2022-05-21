from dataclasses import dataclass
from typing import List


@dataclass
class EAEngineFacade:
    stopping_conditions: dict
    population_size: int
    selection_method: str
    crossover_method: str
    mutations: List[str]
