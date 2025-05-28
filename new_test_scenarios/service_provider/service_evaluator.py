# scenarios/service_provider/service_evaluator.py

class ServiceQualityEvaluator:
    """Evaluates service quality based on response time and satisfaction."""

    def __init__(self, reserved_value=0.0):
        self.reserved_value = reserved_value

    def __call__(self, outcome):
        """Evaluate a single service outcome."""
        if outcome is None:
            return self.reserved_value

        response_time, satisfaction = outcome
        # Better service = lower response time + higher satisfaction
        time_score = max(0, (60 - response_time) / 60)  # Normalize response time (lower is better)
        satisfaction_score = satisfaction / 10  # Normalize satisfaction (higher is better)
        return 0.6 * time_score + 0.4 * satisfaction_score


class TechnicalSupportEvaluator:
    """Evaluates technical support based on resolution rate and expertise."""

    def __init__(self, reserved_value=0.0):
        self.reserved_value = reserved_value

    def __call__(self, outcome):
        """Evaluate a single technical support outcome."""
        if outcome is None:
            return self.reserved_value

        resolution_rate, expertise_level = outcome
        # Higher resolution rate and expertise level = better utility
        return 0.7 * (resolution_rate / 100) + 0.3 * (expertise_level / 5)


class MaintenanceEvaluator:
    """Evaluates maintenance based on uptime and cost efficiency."""

    def __init__(self, reserved_value=0.0):
        self.reserved_value = reserved_value

    def __call__(self, outcome):
        """Evaluate a single maintenance outcome."""
        if outcome is None:
            return self.reserved_value

        uptime_percentage, cost_efficiency = outcome
        # Higher uptime and cost efficiency = better utility
        return 0.8 * (uptime_percentage / 100) + 0.2 * (cost_efficiency / 5)


class GlobalServiceEvaluator:
    """Global evaluator that considers overall service portfolio balance."""

    def __init__(self, reserved_value=0.0):
        self.reserved_value = reserved_value

    def __call__(self, agreements):
        """Evaluate the complete service portfolio."""
        if not agreements:
            return self.reserved_value

        # Count successful agreements
        successful = sum(1 for agreement in agreements if agreement is not None)

        if successful == 0:
            return self.reserved_value

        # Calculate base utility from coverage
        coverage_ratio = successful / len(agreements)

        # Calculate quality scores for each successful service
        quality_scores = []

        for i, agreement in enumerate(agreements):
            if agreement is None:
                continue

            if i == 0:  # Customer Service
                response_time, satisfaction = agreement
                time_score = max(0, (60 - response_time) / 60)
                satisfaction_score = satisfaction / 10
                service_quality = 0.6 * time_score + 0.4 * satisfaction_score
            elif i == 1:  # Technical Support
                resolution_rate, expertise_level = agreement
                service_quality = 0.7 * (resolution_rate / 100) + 0.3 * (expertise_level / 5)
            elif i == 2:  # Maintenance
                uptime_percentage, cost_efficiency = agreement
                service_quality = 0.8 * (uptime_percentage / 100) + 0.2 * (cost_efficiency / 5)
            else:
                service_quality = 0.5  # Default for unknown services

            quality_scores.append(service_quality)

        # Base utility is average quality weighted by coverage
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
        else:
            avg_quality = 0.0

        base_utility = coverage_ratio * avg_quality

        # Synergy bonus for complete service coverage
        if successful == len(agreements):
            synergy_bonus = 0.2  # 20% bonus for complete coverage
        else:
            synergy_bonus = 0.0

        # Diversity bonus for having multiple high-quality services
        high_quality_services = sum(1 for score in quality_scores if score > 0.7)
        if high_quality_services >= 2:
            diversity_bonus = 0.1 * (high_quality_services - 1)
        else:
            diversity_bonus = 0.0

        final_utility = base_utility + synergy_bonus + diversity_bonus

        return min(1.0, max(0.0, final_utility))