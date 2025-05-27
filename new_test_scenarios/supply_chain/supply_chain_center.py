class SupplyChainEvaluator:
    """Evaluates supply chain utility based on meeting production targets within budget."""

    def __init__(self, reserved_value=0.0, target_steel=200, target_electronics=80,
                 target_packaging=1000, budget_limit=12000):
        self.reserved_value = reserved_value
        self.target_steel = target_steel
        self.target_electronics = target_electronics
        self.target_packaging = target_packaging
        self.budget_limit = budget_limit

        # Quality multipliers
        self.quality_multipliers = {
            'standard': 1.0,
            'premium': 1.2,
            'ultra': 1.5
        }

        # Logistics multipliers
        self.logistics_multipliers = {
            ('standard', 'basic'): 0.8,
            ('standard', 'guaranteed'): 0.9,
            ('standard', 'premium'): 1.0,
            ('express', 'basic'): 0.9,
            ('express', 'guaranteed'): 1.0,
            ('express', 'premium'): 1.1,
            ('priority', 'basic'): 1.0,
            ('priority', 'guaranteed'): 1.1,
            ('priority', 'premium'): 1.2
        }

    def __call__(self, agreements):
        if not agreements or len(agreements) < 4:
            return self.reserved_value

        steel_agreement, electronics_agreement, packaging_agreement, logistics_agreement = agreements

        if any(agreement is None for agreement in agreements):
            return self.reserved_value * 0.3

        # Extract quantities and costs
        steel_qty, steel_quality, steel_price = steel_agreement
        electronics_qty, electronics_quality, electronics_price = electronics_agreement
        packaging_qty, packaging_quality, packaging_price = packaging_agreement
        logistics_speed, logistics_reliability, logistics_cost = logistics_agreement

        # Calculate total cost
        total_cost = steel_price + electronics_price + packaging_price + logistics_cost

        # Budget constraint
        if total_cost > self.budget_limit:
            return max(0.0, 1.0 - (total_cost - self.budget_limit) / self.budget_limit * 2.0)

        # Quantity achievement (minimum required to produce)
        steel_ratio = min(1.0, steel_qty / self.target_steel)
        electronics_ratio = min(1.0, electronics_qty / self.target_electronics)
        packaging_ratio = min(1.0, packaging_qty / self.target_packaging)

        # Production capacity is limited by the lowest ratio
        production_capacity = min(steel_ratio, electronics_ratio, packaging_ratio)

        # Quality bonus
        avg_quality_multiplier = (
                                         self.quality_multipliers[steel_quality] +
                                         self.quality_multipliers[electronics_quality] +
                                         self.quality_multipliers[packaging_quality]
                                 ) / 3

        # Logistics multiplier
        logistics_key = (logistics_speed, logistics_reliability)
        logistics_multiplier = self.logistics_multipliers.get(logistics_key, 1.0)

        # Cost efficiency bonus
        cost_efficiency = (self.budget_limit - total_cost) / self.budget_limit * 0.2

        return min(1.0, production_capacity * avg_quality_multiplier * logistics_multiplier + cost_efficiency)