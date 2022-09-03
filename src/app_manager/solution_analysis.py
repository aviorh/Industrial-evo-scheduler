from copy import copy, deepcopy
from typing import Dict

import numpy as np

from src.database.models import SiteData


class SolutionAnalysis:
    @staticmethod
    def get_product_lines_utilization(raw_solution: np.ndarray, site_data: SiteData) -> Dict[int, float]:
        result = {}
        for prd_line in site_data.json_data['production_lines']:
            total_line_schedule = np.zeros(shape=(site_data.total_working_hours,), dtype=int)
            for product in site_data.json_data['products']:
                total_line_schedule = total_line_schedule | raw_solution[prd_line['id'], product['id'], :]
            result[prd_line['id']] = round((int(total_line_schedule.sum()) / site_data.total_working_hours) * 100, 3)

        return result

    @staticmethod
    def get_achieved_forecast(raw_solution: np.ndarray, site_data: SiteData) -> Dict[int, float]:
        result = {}
        products_forecast = {p['id']: p['forecast'] - p['stock'] for p in site_data.json_data['products']}
        products_weight_kg = {p['id']: (p['weight'] / 1000) for p in site_data.json_data['products']}
        lines_prod_rate = {l['id']: l['production_rate'] for l in site_data.json_data['production_lines']}

        for pid, forecast in products_forecast.items():
            actual_units_produced, _ = SolutionAnalysis._get_actual_units_and_kg_produced(pid, lines_prod_rate,
                                                                                       products_weight_kg[pid], raw_solution)
            result[pid] = round((actual_units_produced / forecast) * 100, 3)
        return result

    @staticmethod
    def get_raw_materials_usage(raw_solution: np.ndarray, site_data: SiteData) -> Dict[str, float]:
        raw_materials_stock = copy(site_data.json_data['raw_materials_stock'])

        result = {material_id: 0 for material_id in raw_materials_stock.keys()}

        bulk_products_recipe = deepcopy(site_data.json_data['recipes'])
        lines_prod_rate = {l['id']: l['production_rate'] for l in site_data.json_data['production_lines']}

        for prd in site_data.json_data['products']:
            _, kg_produced = SolutionAnalysis._get_actual_units_and_kg_produced(prd['id'], lines_prod_rate,
                                                                                prd['weight'], raw_solution)
            prd_recipe = bulk_products_recipe[str(prd['bulk_id'])]
            for material_id, needed_amount_per_kg in prd_recipe.items():
                result[material_id] += ((needed_amount_per_kg * kg_produced) / raw_materials_stock[material_id]) * 100
                result[material_id] = round(result[material_id], 3)
        return result

    @staticmethod
    def _get_actual_units_and_kg_produced(product_id, lines_prod_rate, product_unit_weight, raw_solution) -> (int, float):
        actual_kg_produced = 0
        for line_id in lines_prod_rate.keys():
            actual_kg_produced += int(raw_solution[line_id, product_id, :].sum()) * lines_prod_rate[line_id]
        actual_units_produced = round(actual_kg_produced / product_unit_weight)
        return actual_units_produced, actual_kg_produced
