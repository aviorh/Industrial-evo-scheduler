from dataclasses import dataclass
from typing import List


@dataclass
class EAEngineFacade:
    max_generations: int
    population_size: int
    selection_method: str
    crossover_method: str
    mutations: List[str]
