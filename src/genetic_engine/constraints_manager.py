import logging
import numpy as np

from src.genetic_engine.site_manager import SiteManager

logger = logging.getLogger()


class ConstraintsManager:
    def __init__(self, site_manager: SiteManager, invalid_scheduling_penalty, hard_constraints_penalty, soft_constraints_penalty):
        self.soft_constraints_penalty = soft_constraints_penalty
        self.site_manager = site_manager
        self.invalid_scheduling_penalty = invalid_scheduling_penalty
        self.hard_constraints_penalty = hard_constraints_penalty

        self.num_production_lines = len(self.site_manager.production_lines)
        self.num_working_hours = self.site_manager.total_working_hours
        self.num_products = len(self.site_manager.products)

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

    def count_total_down_time(self, schedule) -> int:
        schedule = schedule.view(dtype=np.ndarray)
        pass

    def validate_transition_time(self, schedule) -> int:
        schedule = schedule.view(dtype=np.ndarray)
        pass

    def forecast_compliance(self, schedule):
        schedule = schedule.view(dtype=np.ndarray)
        pass

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


