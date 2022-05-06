from dataclasses import dataclass, field, asdict
from datetime import datetime

from src.genetic_engine.ea_engine import EAEngine


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

    def to_json(self):
        dikt = asdict(self)
        del dikt['schedule']
        return dikt

