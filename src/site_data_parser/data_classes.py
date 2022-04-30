import numpy as np

from typing import Dict, List, Tuple
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass
class Base:
    pass


@dataclass_json
@dataclass
class ProductionLine(Base):
    id: int
    productIds: Dict[int, float]  # bulk product id to capacity (kg/hour) per product. might need packaging capacity
    manpower: int
    setupTime: float  # time to setup the production line once per day of work
    ffo: int


@dataclass_json
@dataclass
class BulkProduct(Base):
    """Bissli Grill"""
    id: int
    recipeId: int
    transitionTime: float  # when transitioning between different HALBs.
    productionLineIds: List[int]  # production lines that can produce this bulk product


@dataclass_json
@dataclass
class Product(Base):
    """Bissli Grill 100g"""
    id: int
    bulk_id: int  # fixme: might need to hold BulkProduct instance for mutation
    name: str
    priority: int  # 1 - 5 / low (1) - urgent (5)
    weight: int  # weight per unit, grams
    stock: int  # num packaged units, in thousands
    forecast: int  # num packaged units, in thousands
    unit_package_id: int
    retailer_package_id: int

    def get_amount_to_produce(self) -> float:
        """:return: amount of product to be produced on a week's course in Kg"""
        return (self.weight * ((self.forecast - self.stock) * 1000)) / 1000.0


@dataclass_json
@dataclass
class SiteData:
    # def __init__(self, production_lines: List[ProductionLine], products: List[Product], bulk_products: List[BulkProduct],
    #              usual_start_hour: int, usual_end_hour: int,
    #              total_working_hours, num_shifts, shift_duration, manpower_per_production_line: Dict[int, int], recipes: Dict[int, Dict],
    #              product_packaging_unit: Dict[int, int], retailer_packaging_unit: Dict[int, Tuple[int, int]]):
    """
    ~~~~~~~ READ ONLY CLASS ~~~~~~~

    :param production_lines: list of production lines
    :param products: list of products
    :param num_shifts: number of shifts per day
    :param usual_start_hour: usual start hour of the site on a regular day
    :param usual_end_hour: usual end hour of the site on a regular day
    :param shift_duration:
    :param recipes: recipe-id -> dictionary containing all ingredients and quantities
    :param rawMaterialsStock: raw material id -> raw material existing stock in kgs
    :param product_packaging_unit: package id -> existing stock quantity. ex: Bissli Grill 100g unit package
    :param retailer_packaging_unit: packagge id -> existing stock quantity. ex: Cardboard-box Bissli Grill 100g 1 unit package
    """
    id: int
    productionLines: List[ProductionLine]
    products: List[Product]
    bulkProducts: List[BulkProduct]

    usualStartHour: int
    usualEndHour: int
    numShifts: int
    shiftDuration: int
    totalWorkingHours: int

    recipes: Dict[int, Dict]
    rawMaterialsStock: Dict[str, int]
    productPackagingUnit: Dict[int, int]
    retailerPackagingUnit: Dict[int, Tuple[int, int]]

    def get_individual_dimensions(self):
        """
        this is a 3D array, where
        x - production_lines
        y - products
        z - total hours (for example hour number 30 is Monday, 6:00 AM
        """
        return len(self.production_lines), len(self.products), self.total_working_hours

    def get_individual_length(self):
        a, b, c = self.get_individual_dimensions()
        return a * b * c

    def print_schedule(self, schedule: np.ndarray):
        schedule = schedule.view(dtype=np.ndarray)
        for prod_line in range(schedule.shape[0]):
            sched_per_line = np.zeros(shape=(schedule.shape[2],), dtype=int)
            for prod_id in range(schedule.shape[1]):
                sched_per_prod = schedule[prod_line, prod_id, :]
                sched_per_line = np.add(sched_per_line, sched_per_prod)
            print(f"prod line: {prod_line} | [{sched_per_line}]")