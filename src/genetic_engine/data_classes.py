from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Base:
    pass


class ProductionLine(Base):
    id: int
    product_ids: Dict[int, int]  # bulk product id to capacity (kg/hour) per product. might need packaging capacity
    manpower: int
    setup_time: float
    ffo: int


@dataclass
class BulkProduct(Base):
    """Bissli Grill"""
    id: int
    recipe_id: int
    cleaning_time: float
    production_line_ids: List[int]  # production lines that can produce this bulk product


@dataclass
class Product(Base):
    """Bissli Grill 100g"""
    id: int
    bulk_id: int  # fixme: might need to hold BulkProduct instance for mutation
    name: str
    priority: int  # 1 - 10 / low - urgent
    weight: int  # grams
    stock: int
    forecast: int  # what needs to be produced over a week's course
    unit_package_id: int
    retailer_package_id: int
