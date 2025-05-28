# scenarios/multi_project/project_combiner.py
from anl2025.ufun import UtilityCombiningCenterUFun
import numpy as np


class ProjectPortfolioCombiner(UtilityCombiningCenterUFun):
    """
    Combines project utilities using a sophisticated portfolio approach.

    This combiner considers:
    - Risk diversification across projects
    - Synergy effects between projects
    - Resource allocation efficiency
    """

    def combine(self, values):
        """
        Combines utilities from multiple projects.

        Args:
            values: List of utilities from each project

        Returns:
            Combined portfolio utility
        """
        if not values:
            return self.reserved_value

        # Base utility is weighted average
        base_utility = np.mean(values)

        # Risk diversification bonus (higher when projects have different performance)
        if len(values) > 1:
            diversity_bonus = np.std(values) * 0.1  # Bonus for portfolio diversity
        else:
            diversity_bonus = 0.0

        # Synergy bonus for having multiple successful projects
        successful_projects = sum(1 for v in values if v > 0.6)
        if successful_projects >= 2:
            synergy_bonus = 0.1 * (successful_projects - 1)
        else:
            synergy_bonus = 0.0

        # Penalty for having any failed projects
        failed_projects = sum(1 for v in values if v < 0.3)
        failure_penalty = 0.15 * failed_projects

        final_utility = base_utility + diversity_bonus + synergy_bonus - failure_penalty

        return max(0.0, min(1.0, final_utility))