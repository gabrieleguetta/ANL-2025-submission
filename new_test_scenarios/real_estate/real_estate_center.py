class RealEstateEvaluator:
    """Evaluates real estate portfolio utility based on diversification and total value."""

    def __init__(self, reserved_value=0.0, target_portfolio_value=2000000):
        self.reserved_value = reserved_value
        self.target_portfolio_value = target_portfolio_value

        # Location multipliers
        self.location_multipliers = {
            'poor': 0.8,
            'average': 1.0,
            'good': 1.2,
            'prime': 1.5
        }

        # Condition multipliers
        self.condition_multipliers = {
            'needs_work': 0.8,
            'good': 1.0,
            'excellent': 1.3
        }

        # Development multipliers for land
        self.development_multipliers = {
            'raw': 0.9,
            'zoned': 1.1,
            'permitted': 1.3
        }

        # Diversification bonus weights
        self.property_type_weights = {
            'residential': 0.25,
            'commercial': 0.35,
            'industrial': 0.25,
            'land': 0.15
        }

    def __call__(self, agreements):
        if not agreements:
            return self.reserved_value

        total_value = 0
        property_values = []
        property_types = ['residential', 'commercial', 'industrial', 'land']

        for i, agreement in enumerate(agreements):
            if agreement is None:
                property_values.append(0)
                continue

            if i < 3:  # Regular properties (residential, commercial, industrial)
                value, location, condition = agreement
                adjusted_value = (value *
                                  self.location_multipliers[location] *
                                  self.condition_multipliers[condition])
            else:  # Land with development status
                value, location, development = agreement
                adjusted_value = (value *
                                  self.location_multipliers[location] *
                                  self.development_multipliers[development])

            property_values.append(adjusted_value)
            total_value += adjusted_value

        # Portfolio value achievement
        value_ratio = total_value / self.target_portfolio_value
        if value_ratio <= 1.0:
            value_utility = value_ratio
        else:
            # Slight penalty for over-investment but not as harsh as under-investment
            value_utility = max(0.5, 1.0 - (value_ratio - 1.0) * 0.3)

        # Diversification bonus
        diversification_score = 0
        for i, weight in enumerate(self.property_type_weights.values()):
            if property_values[i] > 0:  # Property type is included
                type_ratio = property_values[i] / total_value if total_value > 0 else 0
                optimal_ratio = weight
                # Bonus for having closer to optimal allocation
                diversification_score += weight * (1.0 - abs(type_ratio - optimal_ratio))

        # Final utility combines value achievement and diversification
        return min(1.0, value_utility * 0.7 + diversification_score * 0.3)