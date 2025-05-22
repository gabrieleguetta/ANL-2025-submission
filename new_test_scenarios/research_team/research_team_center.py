class ResearchTeamEvaluator:
    """Evaluates research team utility based on skill coverage and budget management."""

    def __init__(self, reserved_value=0.0, budget_limit=250000):
        self.reserved_value = reserved_value
        self.budget_limit = budget_limit

        # Role multipliers for skill contribution
        self.role_multipliers = {
            'junior': 1.0,
            'senior': 1.4,
            'lead': 1.8
        }

        # Skill synergy matrix
        self.skill_synergies = {
            ('lead', 'senior', 'senior'): 1.3,
            ('senior', 'senior', 'senior'): 1.2,
            ('lead', 'lead', 'senior'): 1.25,
            ('junior', 'senior', 'senior'): 1.1
        }

    def __call__(self, agreements):
        if not agreements:
            return self.reserved_value

        total_salary = 0
        roles = []

        for agreement in agreements:
            if agreement is None:
                return self.reserved_value * 0.4  # Need full team

            salary, role = agreement
            total_salary += salary
            roles.append(role)

        # Budget constraint
        if total_salary > self.budget_limit:
            return max(0.0, 1.0 - (total_salary - self.budget_limit) / self.budget_limit)

        # Team capability score
        capability_score = sum(self.role_multipliers[role] for role in roles) / 3

        # Synergy bonus
        role_tuple = tuple(sorted(roles, reverse=True))  # Sort for consistent lookup
        synergy_multiplier = self.skill_synergies.get(role_tuple, 1.0)

        # Budget efficiency bonus
        budget_efficiency = (self.budget_limit - total_salary) / self.budget_limit * 0.1

        return min(1.0, capability_score * synergy_multiplier + budget_efficiency)