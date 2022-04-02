from typing import Dict, List

from src.genetic_engine.data_classes import ProductionLine, Product, BulkProduct


class SiteManager:
    def __init__(self, production_lines: List[ProductionLine], products: List[Product], bulk_products: List[BulkProduct],
                 num_shifts, shift_duration, manpower_per_production_line, recipes: Dict[int, Dict],
                 product_packaging_unit: Dict[int, int], retailer_packaging_unit: Dict[int, int]):
        """

        :param production_lines: list of production lines
        :param products: list of products
        :param num_shifts:
        :param shift_duration:
        :param manpower_per_production_line: production-line-id -> manpower needed to operate
        :param recipes: recipe-id -> dictionary containing all ingredients and quantities
        :param product_packaging_unit: package id -> quantity. ex: Bissli Grill 100g unit package
        :param retailer_packaging_unit: packagge id -> quantity. ex: Cardboard-box Bissli Grill 100g 1 unit package
        """
        self.production_lines = production_lines
        self.products = products
        self.bulk_products = bulk_products

        self.num_shifts = num_shifts
        self.shift_duration = shift_duration
        self.manpower_per_production_line = manpower_per_production_line

        self.recipes = recipes
        self.product_packaging_unit = product_packaging_unit
        self.retailer_packaging_unit = retailer_packaging_unit
