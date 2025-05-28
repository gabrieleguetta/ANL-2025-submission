# scenarios/supply_chain_flat/flat_evaluator.py
from anl2025.ufun import MaxCenterUFun


def create_base_center_ufun():
    """Creates the base center ufun to be flattened."""

    # This would normally be a complex center ufun
    # For demonstration, we'll create a simple max-based evaluator
    def supply_chain_evaluator(agreements):
        if not agreements:
            return 0.0
        # Simple evaluation: average of non-None agreements
        valid_agreements = [a for a in agreements if a is not None]
        if not valid_agreements:
            return 0.0

        total_utility = 0.0
        for agreement in valid_agreements:
            # Each agreement is (delivery_time, quality, cost)
            delivery_score = max(0, (30 - agreement[0]) / 30)  # Faster is better
            quality_score = agreement[1] / 5  # Higher quality is better
            cost_score = max(0, (1000 - agreement[2]) / 1000)  # Lower cost is better
            total_utility += 0.4 * delivery_score + 0.3 * quality_score + 0.3 * cost_score

        return total_utility / len(valid_agreements)

    return supply_chain_evaluator