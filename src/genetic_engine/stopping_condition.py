from dataclasses import dataclass


@dataclass
class StoppingCondition:
    applied: bool
    bound: int
    progress: int = 0
