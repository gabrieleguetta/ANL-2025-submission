"""
**Submitted to ANAC 2025 Automated Negotiation League**
*Team* Unified Strategy Team
*Authors* Combined approach from JobHunterNegotiator and DinnersNegotiator

This code merges the pattern analysis from DinnersNegotiator with the time-based
concession strategy from JobHunterNegotiator to create a robust, general-purpose agent.
"""

import itertools
from typing import List, Tuple, Optional, Dict, Any
from negmas.outcomes import Outcome
from negmas import ResponseType
from anl2025.negotiator import ANL2025Negotiator
from anl2025.ufun import SideUFun
from negmas.sao.controllers import SAOState

from .helpers.helperfunctions import (
    set_id_dict, did_negotiation_end, is_edge_agent,
    get_agreement_at_index, get_current_negotiation_index,
    get_outcome_space_from_index, all_possible_bids_with_agreements_fixed,
    find_best_bid_in_outcomespace
)


class UnifiedNegotiator(ANL2025Negotiator):
    """
    A unified negotiation agent that combines:
    1. Pattern analysis and strategic planning (from DinnersNegotiator)
    2. Time-based concession and opponent modeling (from JobHunterNegotiator)
    3. Adaptive strategy selection based on scenario characteristics
    """

    def init(self):
        """Initialize the agent with comprehensive strategy components."""
        # Core negotiation tracking
        self.current_neg_index = -1
        self.agreements = []
        self.target_bid = None

        # Negotiation mapping
        self.id_dict = {}
        set_id_dict(self)
        self.num_negotiations = len(self.id_dict)

        # Pattern analysis (from DinnersNegotiator)
        self.best_patterns = {}
        self.utility_patterns_by_agreement_count = {}
        self.optimal_pattern = None
        self.optimal_utility = float('-inf')

        # Opponent modeling and concession (from JobHunterNegotiator)
        self.opponent_selections = []
        self.opponent_concession_rate = 0.0
        self.options_by_utilities = []
        self.options_by_opponent_utilities = []

        # Adaptive strategy parameters
        self.scenario_characteristics = {}
        self.is_conservative_scenario = False
        self.time_pressure_threshold = 0.7
        self.min_acceptable_utility_ratio = 0.6

        # Performance tracking
        self.round_number = 0
        self.current_side_ufun = None

        # Initialize strategy based on role
        if not is_edge_agent(self):
            self._analyze_scenario_and_compute_patterns()

    def _analyze_scenario_and_compute_patterns(self):
        """Analyze scenario characteristics and compute optimal patterns."""
        try:
            # Analyze scenario structure
            self._detect_scenario_characteristics()

            # Compute optimal utility patterns
            self._compute_comprehensive_patterns()

        except Exception as e:
            # Fallback to simple strategy if analysis fails
            self.optimal_pattern = None
            self._fallback_to_simple_strategy()

    def _detect_scenario_characteristics(self):
        """Detect key characteristics of the current scenario."""
        self.scenario_characteristics = {
            'num_negotiations': self.num_negotiations,
            'has_multiple_issues': False,
            'is_sequential': True,
            'is_target_oriented': False,
            'is_competitive': True
        }

        # Analyze first negotiation to understand structure
        if self.num_negotiations > 0:
            first_neg_id = self.id_dict.get(0)
            if first_neg_id:
                try:
                    outcomes = get_outcome_space_from_index(self, 0)
                    if outcomes and len(outcomes) > 0:
                        sample_outcome = outcomes[0]
                        if sample_outcome and hasattr(sample_outcome, '__len__'):
                            self.scenario_characteristics['has_multiple_issues'] = len(sample_outcome) > 1
                except:
                    pass

        # Set conservative flag for certain scenario types
        self.is_conservative_scenario = (
                self.num_negotiations <= 3 or
                not self.scenario_characteristics['has_multiple_issues']
        )

    def _compute_comprehensive_patterns(self):
        """Compute optimal patterns using comprehensive analysis."""
        if is_edge_agent(self):
            return

        # Get all possible outcome combinations
        outcome_spaces = []
        for i in range(self.num_negotiations):
            try:
                outcomes = get_outcome_space_from_index(self, i)
                outcomes = outcomes + [None]  # Add disagreement option
                outcome_spaces.append(outcomes)
            except:
                outcome_spaces.append([None])

        if not outcome_spaces:
            return

        # Analyze patterns grouped by number of agreements
        patterns_by_count = {}
        for agreement_count in range(self.num_negotiations + 1):
            patterns_by_count[agreement_count] = []

        # Evaluate all possible combinations
        try:
            for combo in itertools.product(*outcome_spaces):
                agreement_count = sum(1 for outcome in combo if outcome is not None)
                utility = self.ufun(combo)

                patterns_by_count[agreement_count].append((combo, utility))
        except:
            # Fallback if combination space is too large
            self._sample_based_pattern_analysis(outcome_spaces, patterns_by_count)

        # Find best pattern for each agreement count
        for count, patterns in patterns_by_count.items():
            if patterns:
                best_pattern = max(patterns, key=lambda x: x[1])
                self.utility_patterns_by_agreement_count[count] = best_pattern

        # Set overall optimal pattern
        if self.utility_patterns_by_agreement_count:
            best_count, best_pattern = max(
                self.utility_patterns_by_agreement_count.items(),
                key=lambda x: x[1][1]
            )
            self.optimal_pattern = best_pattern[0]
            self.optimal_utility = best_pattern[1]

    def _sample_based_pattern_analysis(self, outcome_spaces, patterns_by_count):
        """Fallback pattern analysis using sampling for large spaces."""
        import random

        # Sample combinations instead of exhaustive search
        max_samples = 1000
        samples = 0

        while samples < max_samples:
            try:
                combo = tuple(random.choice(space) for space in outcome_spaces)
                agreement_count = sum(1 for outcome in combo if outcome is not None)
                utility = self.ufun(combo)

                patterns_by_count[agreement_count].append((combo, utility))
                samples += 1
            except:
                break

    def _fallback_to_simple_strategy(self):
        """Fallback to simple strategy if pattern analysis fails."""
        try:
            self.optimal_pattern = find_best_bid_in_outcomespace(self)
        except:
            self.optimal_pattern = None

    def propose(self, negotiator_id: str, state: SAOState, dest: str = None) -> Outcome:
        """Generate strategic proposals combining pattern analysis and concession."""
        # Update strategy if new negotiation started
        if did_negotiation_end(self):
            self._start_new_negotiation_round(negotiator_id)
            self._update_comprehensive_strategy()

        # Get negotiation progress
        relative_time = self._get_relative_time(negotiator_id, state)

        # Generate bid based on agent role
        if is_edge_agent(self):
            return self._generate_edge_proposal(negotiator_id, relative_time)
        else:
            return self._generate_center_proposal(negotiator_id, relative_time)

    def _generate_center_proposal(self, negotiator_id: str, relative_time: float) -> Outcome:
        """Generate center agent proposals using pattern analysis + concession."""
        current_neg_idx = get_current_negotiation_index(self)

        # Early phase: stick to optimal pattern
        if relative_time < 0.3 and self.optimal_pattern and current_neg_idx < len(self.optimal_pattern):
            target_outcome = self.optimal_pattern[current_neg_idx]
            if target_outcome is not None:
                return target_outcome

        # Special handling for conservative scenarios (like dinners)
        if self.is_conservative_scenario:
            return self._generate_conservative_proposal(current_neg_idx, relative_time)

        # General concession strategy
        return self._generate_concession_based_proposal(relative_time)

    def _generate_conservative_proposal(self, current_neg_idx: int, relative_time: float) -> Outcome:
        """Conservative strategy for scenarios like dinners."""
        # Check if we should avoid more agreements
        current_agreement_count = sum(1 for a in self.agreements if a is not None)

        # For 3-negotiation scenarios, be selective about additional agreements
        if self.num_negotiations == 3 and current_neg_idx == 2 and current_agreement_count >= 2:
            if relative_time > 0.4:
                return None  # End negotiation

        # Use pattern-based proposal
        if self.optimal_pattern and current_neg_idx < len(self.optimal_pattern):
            return self.optimal_pattern[current_neg_idx]

        return self._find_best_contextual_outcome()

    def _generate_concession_based_proposal(self, relative_time: float) -> Outcome:
        """Generate proposals using time-based concession."""
        if not self.options_by_utilities:
            return self._find_best_contextual_outcome()

        # Boulware-style concession: slow at first, faster later
        concession_factor = pow(relative_time, 1 / 3)

        # Find proposal based on concession level
        if relative_time < 0.4:
            # Early: aim for best outcomes
            best_outcomes = [opt for opt in self.options_by_utilities[-10:]]
            if best_outcomes:
                return best_outcomes[-1][3]  # Return the bid part

        # Later: concede gradually
        acceptable_threshold = self.min_acceptable_utility_ratio * concession_factor
        acceptable_options = [
            opt for opt in self.options_by_utilities
            if opt[1] >= acceptable_threshold * self.optimal_utility
        ]

        if acceptable_options:
            # Choose from acceptable options, considering opponent utility
            return max(acceptable_options, key=lambda x: x[2])[3]

        return self._find_best_contextual_outcome()

    def _generate_edge_proposal(self, negotiator_id: str, relative_time: float) -> Outcome:
        """Generate edge agent proposals using utility maximization + concession."""
        # Find best outcome
        try:
            worst_bid, best_bid = self.ufun.extreme_outcomes()
        except:
            # Fallback if extreme_outcomes fails
            outcomes = get_outcome_space_from_index(self, 0)
            if outcomes:
                best_bid = max(outcomes, key=lambda x: self.ufun(x) if x else 0)
            else:
                return None

        # Time-based concession for edge agents
        if relative_time < 0.5:
            return best_bid

        # Later in negotiation, consider conceding
        if self.options_by_utilities:
            concession_level = int(len(self.options_by_utilities) * (1 - relative_time))
            concession_level = max(0, min(concession_level, len(self.options_by_utilities) - 1))
            return self.options_by_utilities[-(concession_level + 1)][3]

        return best_bid

    def respond(self, negotiator_id: str, state: SAOState, source: str = None) -> ResponseType:
        """Multi-criteria acceptance decision."""
        if did_negotiation_end(self):
            self._start_new_negotiation_round(negotiator_id)
            self._update_comprehensive_strategy()

        if state.current_offer is None:
            return ResponseType.REJECT_OFFER

        # Track opponent behavior
        if self.options_by_opponent_utilities:
            try:
                offer_idx = self._get_offer_utility_index(state.current_offer)
                if offer_idx is not None:
                    self.opponent_selections.append(offer_idx)
            except:
                pass

        # Multi-criteria acceptance decision
        return self._make_comprehensive_acceptance_decision(negotiator_id, state)

    def _make_comprehensive_acceptance_decision(self, negotiator_id: str, state: SAOState) -> ResponseType:
        """Make acceptance decision using multiple criteria."""
        offer = state.current_offer
        relative_time = self._get_relative_time(negotiator_id, state)

        if is_edge_agent(self):
            return self._edge_acceptance_decision(offer, relative_time)
        else:
            return self._center_acceptance_decision(offer, relative_time)

    def _center_acceptance_decision(self, offer: Outcome, relative_time: float) -> ResponseType:
        """Center agent acceptance logic."""
        current_neg_idx = get_current_negotiation_index(self)

        # Pattern matching acceptance
        if (self.optimal_pattern and
                current_neg_idx < len(self.optimal_pattern) and
                offer == self.optimal_pattern[current_neg_idx]):
            return ResponseType.ACCEPT_OFFER

        # Conservative scenario logic
        if self.is_conservative_scenario:
            current_agreement_count = sum(1 for a in self.agreements if a is not None)

            # For 3-negotiation scenarios with 2+ agreements, be very selective
            if (self.num_negotiations == 3 and
                    current_neg_idx == 2 and
                    current_agreement_count >= 2):
                return ResponseType.REJECT_OFFER

        # Utility-based acceptance
        utility_with_offer = self._calculate_offer_utility(offer)
        utility_without_offer = self._calculate_no_agreement_utility()

        # Time-pressure acceptance
        if relative_time > self.time_pressure_threshold:
            if utility_with_offer > utility_without_offer * 1.1:
                return ResponseType.ACCEPT_OFFER

        # Strategic acceptance based on improvement
        if relative_time > 0.4:
            improvement = utility_with_offer - utility_without_offer
            if improvement > 0:
                return ResponseType.ACCEPT_OFFER

        return ResponseType.REJECT_OFFER

    def _edge_acceptance_decision(self, offer: Outcome, relative_time: float) -> ResponseType:
        """Edge agent acceptance logic."""
        offer_utility = self.ufun(offer)

        # Get best possible utility
        try:
            _, best_outcome = self.ufun.extreme_outcomes()
            best_utility = self.ufun(best_outcome)
        except:
            best_utility = 1.0

        # Time-based acceptance thresholds
        if relative_time < 0.4:
            threshold = 0.95
        elif relative_time < 0.7:
            threshold = 0.8
        elif relative_time < 0.9:
            threshold = 0.6
        else:
            threshold = 0.4

        if offer_utility >= threshold * best_utility:
            return ResponseType.ACCEPT_OFFER

        # Always accept if above reservation value and late in negotiation
        if relative_time > 0.9 and offer_utility > self.ufun.reserved_value:
            return ResponseType.ACCEPT_OFFER

        return ResponseType.REJECT_OFFER

    def _start_new_negotiation_round(self, negotiator_id: str):
        """Initialize new negotiation round."""
        self.round_number = len(self.finished_negotiators)
        self.opponent_selections = []

        # Get side utility function for center agents
        if not is_edge_agent(self):
            try:
                _, context = self.negotiators[negotiator_id]
                self.current_side_ufun = context.get("ufun")
            except:
                self.current_side_ufun = None

    def _update_comprehensive_strategy(self):
        """Update strategy combining both approaches."""
        # Update agreements list
        self._update_agreements_list()

        # Compute current possibilities and utilities
        if is_edge_agent(self):
            self._update_edge_strategy()
        else:
            self._update_center_strategy()

    def _update_agreements_list(self):
        """Update the agreements list with latest results."""
        prev_index = self.current_neg_index - 1
        if prev_index >= 0:
            try:
                agreement = get_agreement_at_index(self, prev_index)
                while len(self.agreements) <= prev_index:
                    self.agreements.append(None)
                self.agreements[prev_index] = agreement
            except:
                pass

    def _update_edge_strategy(self):
        """Update strategy for edge agents."""
        try:
            outcomes = get_outcome_space_from_index(self, 0)
            if self.current_side_ufun:
                utils = [
                    (outcome, self.ufun(outcome), self.current_side_ufun(outcome), outcome)
                    for outcome in outcomes if outcome is not None
                ]
                self._order_utilities(utils)

            _, self.target_bid = self.ufun.extreme_outcomes()
        except:
            self.target_bid = None

    def _update_center_strategy(self):
        """Update strategy for center agents."""
        try:
            current_possibilities = all_possible_bids_with_agreements_fixed(self)
            current_neg_idx = get_current_negotiation_index(self)

            if self.current_side_ufun and current_possibilities:
                utils = [
                    (outcome, self.ufun(outcome),
                     self.current_side_ufun(outcome[current_neg_idx]) if current_neg_idx < len(outcome) else 0,
                     outcome[current_neg_idx] if current_neg_idx < len(outcome) else None)
                    for outcome in current_possibilities
                ]
                self._order_utilities(utils)

            self.target_bid = find_best_bid_in_outcomespace(self)
        except:
            self.target_bid = None

    def _order_utilities(self, utilities: List[Tuple]):
        """Order utilities for decision making."""
        self.options_by_utilities = sorted(utilities, key=lambda x: x[1])
        self.options_by_opponent_utilities = sorted(utilities, key=lambda x: x[2])

    def _get_relative_time(self, negotiator_id: str, state: SAOState) -> float:
        """Get relative time in negotiation."""
        try:
            nmi = self.negotiators[negotiator_id].negotiator.nmi
            if state.step == 0:
                return 0.0
            if nmi.n_steps and state.step >= nmi.n_steps - 1:
                return 1.0
            return state.relative_time if state.relative_time is not None else 0.0
        except:
            return 0.0

    def _calculate_offer_utility(self, offer: Outcome) -> float:
        """Calculate utility if offer is accepted."""
        try:
            test_agreements = self.agreements.copy()
            current_neg_idx = get_current_negotiation_index(self)

            while len(test_agreements) <= current_neg_idx:
                test_agreements.append(None)

            test_agreements[current_neg_idx] = offer

            # Pad with None for remaining negotiations
            while len(test_agreements) < self.num_negotiations:
                test_agreements.append(None)

            return self.ufun(tuple(test_agreements))
        except:
            return 0.0

    def _calculate_no_agreement_utility(self) -> float:
        """Calculate utility if no agreement is reached."""
        try:
            test_agreements = self.agreements.copy()
            current_neg_idx = get_current_negotiation_index(self)

            while len(test_agreements) <= current_neg_idx:
                test_agreements.append(None)

            test_agreements[current_neg_idx] = None

            # Pad with None for remaining negotiations
            while len(test_agreements) < self.num_negotiations:
                test_agreements.append(None)

            return self.ufun(tuple(test_agreements))
        except:
            return 0.0

    def _find_best_contextual_outcome(self) -> Outcome:
        """Find best outcome in current context."""
        try:
            if is_edge_agent(self):
                _, best_outcome = self.ufun.extreme_outcomes()
                return best_outcome
            else:
                return find_best_bid_in_outcomespace(self)
        except:
            return None

    def _get_offer_utility_index(self, offer: Outcome) -> Optional[int]:
        """Get index of offer in utility rankings."""
        try:
            for i, option in enumerate(self.options_by_opponent_utilities):
                if option[3] == offer:
                    return i
        except:
            pass
        return None


# Test runner
if __name__ == "__main__":
    from .helpers.runner import run_a_tournament

    run_a_tournament(UnifiedNegotiator, small=True)