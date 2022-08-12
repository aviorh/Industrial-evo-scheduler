from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class EAEngineFacade:
    """
    {
        "site_data_id": int,
        "population_size": int,
        "stopping_conditions_configuration": {
            "TIME_STOPPING_CONDITION": {"applied": False, "bound": 0},
            "FITNESS_STOPPING_CONDITION": {"applied": False, "bound": 0},
            "GENERATIONS_STOPPING_CONDITION": {"applied": True, "bound": DEFAULT_GENERATIONS}
        },
        "selection_method": {"method_id": 1, "params": {"a": "a", "b": "b"}},
        "crossover_method": {"method_id": 1, "params": {"a": "a", "b": "b"}},
        "mutations": [{"mutation_id": 0, "params": {"a": "a", "b": "b"}},
                      {"mutation_id": 1, "params": {"c": "a"}}]
    }
    """

    site_data_id: int
    population_size: int
    stopping_conditions_configuration: Dict[str, Dict]
    selection_method: Dict
    crossover_method: Dict
    mutations: List[Dict]

    def to_dict(self):
        return asdict(self)