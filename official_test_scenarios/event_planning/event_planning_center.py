import pandas as pd
from pathlib import Path


class EventPlanningEvaluator:
    """Evaluates the center utility for event planning based on budget management and service synergy."""

    def __init__(self, reserved_value=0.0, target_budget=45000):
        self.reserved_value = reserved_value
        self.target_budget = target_budget

        # Service level synergy multipliers
        self.synergy_bonus = {
            ('luxury', 'luxury', 'luxury', 'luxury', 'luxury'): 1.3,
            ('premium', 'premium', 'premium', 'premium', 'premium'): 1.15,
            ('basic', 'basic', 'basic', 'basic', 'basic'): 1.0
        }

    def __call__(self, agreements):
        if not agreements:
            return self.reserved_value

        # Calculate total budget spent
        total_budget = 0
        service_levels = []

        for agreement in agreements:
            if agreement is None:
                return self.reserved_value * 0.5  # Penalty for incomplete planning

            budget, service_level = agreement
            total_budget += budget
            service_levels.append(service_level)

        # Budget efficiency (closer to target is better)
        budget_ratio = total_budget / self.target_budget
        if budget_ratio <= 1.0:
            budget_utility = 1.0 - abs(1.0 - budget_ratio) * 0.5
        else:
            budget_utility = max(0.0, 1.0 - (budget_ratio - 1.0) * 2.0)  # Heavy penalty for overspend

        # Service level synergy
        service_tuple = tuple(service_levels)
        synergy_multiplier = self.synergy_bonus.get(service_tuple, 1.0)

        # Mixed service penalty
        unique_services = len(set(service_levels))
        if unique_services > 2:
            synergy_multiplier *= 0.8  # Penalty for inconsistent service levels

        return min(1.0, budget_utility * synergy_multiplier)