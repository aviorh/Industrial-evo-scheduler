from typing import Dict, List, Tuple

import numpy as np

from src.genetic_engine.data_classes import ProductionLine, Product, BulkProduct


class SiteManager:
    def __init__(self, production_lines: List[ProductionLine], products: List[Product], bulk_products: List[BulkProduct],
                 total_working_hours, num_shifts, shift_duration, manpower_per_production_line: Dict[int, int], recipes: Dict[int, Dict],
                 product_packaging_unit: Dict[int, int], retailer_packaging_unit: Dict[int, Tuple[int, int]]):
        """

        :param production_lines: list of production lines
        :param products: list of products
        :param num_shifts: number of shifts per day
        :param shift_duration:
        :param manpower_per_production_line: production-line-id -> manpower needed to operate
        :param recipes: recipe-id -> dictionary containing all ingredients and quantities
        :param product_packaging_unit: package id -> quantity. ex: Bissli Grill 100g unit package
        :param retailer_packaging_unit: packagge id -> (quantity, num units per retailer package). ex: Cardboard-box Bissli Grill 100g 1 unit package
        """
        self.production_lines = production_lines
        self.products = products
        self.bulk_products = bulk_products

        self.num_shifts = num_shifts
        self.shift_duration = shift_duration
        self.total_working_hours = total_working_hours
        self.manpower_per_production_line = manpower_per_production_line

        self.recipes = recipes
        self.product_packaging_unit = product_packaging_unit
        self.retailer_packaging_unit = retailer_packaging_unit

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