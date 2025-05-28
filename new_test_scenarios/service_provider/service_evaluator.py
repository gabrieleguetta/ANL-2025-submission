# scenarios/service_provider/service_evaluator.py
def service_quality_evaluator(outcome):
    """Evaluates service quality based on response time and satisfaction."""
    if outcome is None:
        return 0.0
    response_time, satisfaction = outcome
    # Better service = lower response time + higher satisfaction
    time_score = max(0, (60 - response_time) / 60)  # Normalize response time
    satisfaction_score = satisfaction / 10  # Normalize satisfaction
    return 0.6 * time_score + 0.4 * satisfaction_score


def technical_support_evaluator(outcome):
    """Evaluates technical support based on resolution rate and expertise."""
    if outcome is None:
        return 0.0
    resolution_rate, expertise_level = outcome
    # Higher resolution rate and expertise level = better utility
    return 0.7 * (resolution_rate / 100) + 0.3 * (expertise_level / 5)


def maintenance_evaluator(outcome):
    """Evaluates maintenance based on uptime and cost efficiency."""
    if outcome is None:
        return 0.0
    uptime_percentage, cost_efficiency = outcome
    # Higher uptime and cost efficiency = better utility
    return 0.8 * (uptime_percentage / 100) + 0.2 * (cost_efficiency / 5)


def global_service_evaluator(agreements):
    """Global evaluator that considers overall service portfolio balance."""
    if not agreements:
        return 0.0

    # Count successful agreements
    successful = sum(1 for agreement in agreements if agreement is not None)

    # Base utility from number of successful agreements
    base_utility = successful / len(agreements)

    # Bonus for having all services covered
    if successful == len(agreements):
        base_utility *= 1.2

    return min(1.0, base_utility)