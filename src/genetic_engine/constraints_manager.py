import logging
import math
from typing import List

import numpy as np

from src.site_data_parser.data_classes import SiteData

logger = logging.getLogger()


class ConstraintsManager:
    def __init__(self, site_manager: SiteData, invalid_scheduling_penalty, hard_constraints_penalty, soft_constraints_penalty):
        self.soft_constraints_penalty = soft_constraints_penalty
        self.site_manager = site_manager
        self.invalid_scheduling_penalty = invalid_scheduling_penalty
        self.hard_constraints_penalty = hard_constraints_penalty

        self.num_production_lines = len(self.site_manager.production_lines)
        self.num_working_hours = self.site_manager.total_working_hours
        self.num_products = len(self.site_manager.products)

    def count_regular_hours_exceeded_violations(self, schedule) -> int:
        # fixme: finish
        line_schedules = self._get_production_line_schedules(schedule)
        for line_sched in line_schedules:
            day = 0

    def _get_production_line_schedules(self, schedule):
        # get production line schedule
        production_line_schedules = []
        for i in range(self.num_production_lines):
            for j in range(self.num_products):
                if j == 0:
                    prod_line_sched = schedule[i, j, :]
                else:
                    prod_line_sched = prod_line_sched | schedule[i, j, :]
            production_line_schedules.append(prod_line_sched)

        return production_line_schedules

    def count_maximum_product_line_utilization(self, schedule) -> int:
        """
        make sure product line is operating as much as possible during regular working hours.
        check if ANYTHING is produced
        :param schedule:
        :return:
        """
        pass

    def sufficient_packaging_material(self, schedule):
        # fixme: DivisionByZero exception
        current_amounts = self._get_produced_amount_per_product(schedule)
        unit_package_weights = [prod.weight for prod in self.site_manager.products]
        requested_unit_packages = [math.ceil(current_amounts[i] / unit_package_weights[i]) for i in range(self.num_products)]

        amount_units_per_retailer_package = [self.site_manager.retailer_packaging_unit[i][1] for i in self.site_manager.retailer_packaging_unit.keys()]

        requested_retailer_packages = [math.ceil(requested_unit_packages[i] / amount_units_per_retailer_package[i]) for i in range(len(requested_unit_packages))]

        unit_package_ids = [prod.unit_package_id for prod in self.site_manager.products]
        retailer_package_ids = [prod.retailer_package_id for prod in self.site_manager.products]

        unit_package_amounts = [self.site_manager.product_packaging_unit[i] for i in unit_package_ids]
        retailer_package_amounts = [self.site_manager.retailer_packaging_unit[i][0] for i in retailer_package_ids]

        missing_unit_amounts_percentage = [((requested_unit_packages[i] / unit_package_amounts[i])*100) - 100
                                      for i in range(len(requested_unit_packages))]

        missing_retailer_amounts_percentage = [((requested_retailer_packages[i] / retailer_package_amounts[i])*100) - 100
                                      for i in range(len(retailer_package_amounts))]

        missing_amount_violation = sum(i for i in missing_unit_amounts_percentage if i > 0) + \
                                   sum(i for i in missing_retailer_amounts_percentage if i > 0)
        return missing_amount_violation

    def count_total_down_time(self, schedule) -> int:
        # schedule = schedule.view(dtype=np.ndarray)
        pass

    def count_forecast_exceeded_violations(self, schedule) -> int:
        """
        make sure schedule does not exceed product forecast goal.
        the violation is calculated as sum of each product overflow forecast percentage.
        :param schedule:
        :return: number of violations
        """
        # fixme: test
        current_amounts = self._get_produced_amount_per_product(schedule)
        expected_amounts = [prod.get_amount_to_produce() for prod in self.site_manager.products]
        # fixme: assuming product id is a running number
        forecast_percentage_achieved = [(current_amounts[i] / expected_amounts[i])*100 for i in range(len(expected_amounts))]

        violation_score = 0
        for forecast in forecast_percentage_achieved:
            if forecast > 100:
                violation_score += (forecast - 100)  # to get the overflow diff

        return violation_score

    def count_forecast_goal_violations(self, schedule) -> int:
        """
        make sure prioritized products achieve maximum forecast
        'punish' each product which doesn't achieve its forecast goal according to its priority
        the violation is calculated as sum of each product missing forecast percentage * priority
        """
        # fixme: test
        current_amounts = self._get_produced_amount_per_product(schedule)
        expected_amounts = [prod.get_amount_to_produce() for prod in self.site_manager.products]
        # fixme: assuming product id is a running number
        missing_forecast_percentage = [(i, 100 - (current_amounts[i] / expected_amounts[i])*100) for i in range(len(expected_amounts))]

        violation_score = 0
        for tup in missing_forecast_percentage:
            product_priority = self.site_manager.products[tup[0]].priority
            missing_amount = tup[1]
            if missing_amount < 100:  # we dont cover forecast for this product
                violation_score += (missing_amount * product_priority)

        return violation_score

    def ensure_minimal_transition_time(self, schedule) -> int:
        """
        for each production line, promote production sequence of the same product to avoid transition time
        """
        # schedule = schedule.view(dtype=np.ndarray)
        print()

    def overall_forecast_compliance_violations(self, schedule):
        # fixme: need to take setup time and cleaning time into account
        # schedule = schedule.view(dtype=np.ndarray)
        expected_amount = [prod.get_amount_to_produce() for prod in self.site_manager.products]
        current_amount = self._get_produced_amount_per_product(schedule)

        # calculates the missing/overflow share of % in production, each percentage is a violation point
        num_violations = sum([abs(100 - (current_amount[i] / expected_amount[i])*100) for i in range(len(expected_amount))])
        return float(num_violations)

    def _get_produced_amount_per_product(self, schedule) -> List[float]:
        current_amount = [0 for _ in self.site_manager.products]
        for i, j in np.ndindex(self.num_production_lines, self.num_products):
            _sched = schedule[i, j, :]

            # count all 1's sequences * cleaning time and reduce from num_production_hours
            num_transitions = len(np.diff(np.where(np.concatenate(([_sched[0]], _sched[:-1] != _sched[1:], [1])))[0])[::2])
            bulk_id = self.site_manager.products[j].bulk_id
            bulk_transition_time = self.site_manager.bulk_products[bulk_id].transition_time
            num_production_hours = _sched.sum() - (num_transitions * bulk_transition_time)

            prod_line = self.site_manager.production_lines[i]
            amount_kg = prod_line.product_ids.get(str(j), 0) * num_production_hours
            current_amount[j] += amount_kg
        return current_amount

    def production_line_halb_compliance(self, schedule):
        # schedule: np.ndarray = schedule.view(dtype=np.ndarray)

        accepted_products_per_line = [0 for _ in range(self.num_production_lines)]
        for i, line in enumerate(self.site_manager.production_lines):
            accepted_products_per_line[i] = list(line.product_ids.keys())

        num_violations = 0
        for i, j in np.ndindex(self.num_production_lines, self.num_products):
            if j not in accepted_products_per_line[i]:
                num_violations += schedule[i, j, :].sum()

        return num_violations

    def count_overlaying_manufacturing(self, schedule) -> int:
        """
        enforce single product per production line at a time
        this constraint is deprecated
        """
        """
        # schedule is of type Individual, which is actually np.ndarray.view(). this causes issues later.
        # thus, need to convert schedule to np.ndarray
        # schedule = schedule.view(dtype=np.ndarray)

        max_invalidations_per_line = (self.num_products - 1) * self.num_working_hours
        invalidations_arr = [0 for _ in range(self.num_production_lines)]

        for i, j in np.ndindex(self.num_production_lines, self.num_working_hours):
            num_overlaying_products = schedule[i, :, j].sum()
            invalidations_arr[i] += (num_overlaying_products - 1)
            logger.debug(f"production line: {i}, hour: {j}, overlaying: {num_overlaying_products}")

        for i, inv in enumerate(invalidations_arr):
            logger.debug(f"line: {i}, invalidations: {inv}/{max_invalidations_per_line}")

        total_invalidations = sum(invalidations_arr)
        return total_invalidations
        """
        return 0
