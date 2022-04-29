from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Base:
    pass


@dataclass
class ProductionLine(Base):
    id: int
    product_ids: Dict[int, float]  # bulk product id to capacity (kg/hour) per product. might need packaging capacity
    manpower: int
    setup_time: int  # time to setup the production line once per day of work
    ffo: int


@dataclass
class BulkProduct(Base):
    """Bissli Grill"""
    id: int
    recipe_id: int
    transition_time: float  # when transitioning between different HALBs.
    production_line_ids: List[int]  # production lines that can produce this bulk product


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
