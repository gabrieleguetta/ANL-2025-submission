"""
**Submitted to ANAC 2025 Automated Negotiation League**
*Team* type your team name here
*Authors* type your team member names with their emails here

This code is free to use or update given that proper attribution is given to
the authors and the ANAC 2025 ANL competition.
"""
import itertools
from negmas.outcomes import Outcome

from .helpers.helperfunctions import (
    set_id_dict, did_negotiation_end, get_current_negotiation_index,
    is_edge_agent, find_best_bid_in_outcomespace, get_target_bid_at_current_index
)
#be careful: When running directly from this file, change the relative import to an absolute import. When submitting, use relative imports.
#from helpers.helperfunctions import set_id_dict, ...

from anl2025.negotiator import ANL2025Negotiator
from negmas.sao.controllers import SAOController, SAOState
from negmas import ResponseType

class NewNegotiator(ANL2025Negotiator):
    """
    Advanced negotiating agent for ANL 2025 competition that handles both center and edge agent roles.

    Key strategies:
    1. Adaptive coordination strategy for center agent to align agreements across sequential negotiations
    2. Time-dependent concession strategy that adapts based on deadline and opponent behavior
    3. Flexible acceptance strategy with dynamic thresholds
    """


    def init(self):
        """Executed when the agent is created. In ANL2025, all agents are initialized before the tournament starts."""
        #print("init")

        #Initalize variables
        self.current_neg_index = -1
        self.target_bid = None
        self.concession_rate = 0.2  # Controls how quickly we concede (lower = slower)

        # Make a dictionary that maps the index of the negotiation to the negotiator id. The index of the negotiation is the order in which the negotiation happen in sequence.
        self.id_dict = {}
        set_id_dict(self)

        # Track previous offers in current negotiation
        self.received_offers = {}


    def get_negotiation_time(self, state):
        """Returns the normalized time (0-1) in the current negotiation."""
        if hasattr(state, 'time') and state.time is not None:
            return state.time
        # If time is not available, approximate based on current step
        if hasattr(state, 'n_steps') and state.n_steps:
            return min(1.0, state.step / state.n_steps)
        return 0.5  # Default middle value if we can't determine time


    def adaptive_bidding(self, negotiator_id, state):
        """Generate a time-dependent bid based on target and concession rate."""
        nmi = self.negotiators[negotiator_id].negotiator.nmi
        time = self.get_negotiation_time(state)

        # Get target bid for current negotiation
        target_bid = get_target_bid_at_current_index(self)

        # If we're early in the negotiation, stick to our target
        if time < 0.3:
            return target_bid

        # Sample different bids as time progresses
        num_samples = 5 + int(time * 15)  # 5 to 20 samples
        possible_bids = list(nmi.outcome_space.sample(num_samples))

        # Add target bid to candidates
        if target_bid is not None:
            possible_bids.append(target_bid)

        # Find the best bid based on utility
        best_bid = None
        best_utility = float('-inf')

        reserved_value = self.ufun.reserved_value if hasattr(self.ufun, 'reserved_value') else 0.0

        for bid in possible_bids:
            if bid is None:
                continue

            try:
                utility = self.ufun(bid)
                if utility > best_utility:
                    best_utility = utility
                    best_bid = bid
            except Exception:
                # Skip bids that can't be evaluated
                continue

        # If no valid bid found or all are below reserved value, use target
        if best_bid is None or best_utility < reserved_value:
            return target_bid

        return best_bid


    def calculate_acceptance_threshold(self, negotiator_id=None, state=None):
        """Calculate dynamic acceptance threshold based on time and opponent behavior."""

        # Handle the case when state is not provided
        if state is None:
            return 0.7  # Default threshold if no state is provided

        time = self.get_negotiation_time(state)

        # Get reserved value
        reserved_value = self.ufun.reserved_value if hasattr(self.ufun, 'reserved_value') else 0.0

        # Base threshold depends on time remaining
        # More concessions as time passes
        threshold = 1.0 - (time ** (1 / self.concession_rate))

        # Ensure threshold never drops below reserved value
        return max(threshold, reserved_value)


    def propose(
            self, negotiator_id: str, state: SAOState, dest: str | None = None
    ) -> Outcome | None:
        """Proposes to the given partner (dest) using the side negotiator (negotiator_id).

        Remarks:
            - You can use the negotiator_id to identify what side negotiator is currently proposing. This id is stable within a negotiation.
        """
        # If the negotiation has ended, update the strategy. The subnegotiator may of may not have found an agreement: this affects the strategy for the rest of the negotiation.
        if did_negotiation_end(self):
            self._update_strategy()

        # Generate next bid using time-dependent strategy
        bid = self.adaptive_bidding(negotiator_id, state)

        return bid

    def respond(
            self, negotiator_id: str, state: SAOState, source: str | None = None
    ) -> ResponseType:
        """Responds to the given partner (source) using the side negotiator (negotiator_id).

        Remarks:
            - negotiator_id is the ID of the side negotiator representing this agent.
            - source: is the ID of the partner.
            - the mapping from negotiator_id to source is stable within a negotiation.

        """
        if did_negotiation_end(self):
            self._update_strategy()

        # This agent is very stubborn: it only accepts an offer if it is EXACTLY the target bid it wants to have.
        # if state.current_offer is get_target_bid_at_current_index(self):
        #     return ResponseType.ACCEPT_OFFER
        #
        # return ResponseType.REJECT_OFFER
        # You can also return ResponseType.END_NEGOTIATION to end the negotiation.

        # Store received offer for potential analysis
        if negotiator_id not in self.received_offers:
            self.received_offers[negotiator_id] = []

        if state.current_offer is not None:
            self.received_offers[negotiator_id].append(state.current_offer)

        # If no offer or None offer, reject
        if state.current_offer is None:
            return ResponseType.REJECT_OFFER

        # Calculate offer utility safely
        try:
            offer_utility = self.ufun(state.current_offer)
        except Exception:
            # If we can't evaluate the utility, reject
            return ResponseType.REJECT_OFFER

        # Get reserved value
        reserved_value = self.ufun.reserved_value if hasattr(self.ufun, 'reserved_value') else 0.0

        # If below reserved value, always reject
        if offer_utility < reserved_value:
            return ResponseType.REJECT_OFFER

        # Get target bid for this negotiation
        target_bid = get_target_bid_at_current_index(self)

        # If offer matches target bid, accept immediately
        if state.current_offer == target_bid:
            return ResponseType.ACCEPT_OFFER

        # Calculate acceptance threshold - pass both parameters to handle all cases
        threshold = self.calculate_acceptance_threshold(negotiator_id, state)

        # Accept if utility above threshold
        if offer_utility >= threshold:
            return ResponseType.ACCEPT_OFFER

        # Time-pressure acceptance (last 5% of negotiation)
        time = self.get_negotiation_time(state)
        if time > 0.95:
            # In the final moments, accept anything better than 90% of our threshold
            if offer_utility >= threshold * 0.9:
                return ResponseType.ACCEPT_OFFER

        return ResponseType.REJECT_OFFER


    def _update_strategy(self) -> None:
        """Update the strategy of the agent after a negotiation has ended.
               """
        # if your current role is the edge agent, use the strategy as if your centeragent is in it's last subnegotiation.
        # In this case, just get the best bid from the utility function.
        if is_edge_agent(self):
            # note that the edge utility function has a slightly different structure than a center utility function.
            _, best_bid = self.ufun.extreme_outcomes()
            self.target_bid = best_bid
            return

        #get the best bid from the outcomes that are still possible to achieve.
        best_bid = find_best_bid_in_outcomespace(self)
        self.target_bid = best_bid

        #print(self.target_bid)

        # Reset data for the next negotiation
        self.received_offers = {}


# if you want to do a very small test, use the parameter small=True here. Otherwise, you can use the default parameters.
if __name__ == "__main__":
    from helpers.runner import run_a_tournament
    #Be careful here. When running directly from this file, relative imports give an error, e.g. import .helpers.helpfunctions.
    #Change relative imports (i.e. starting with a .) at the top of the file. However, one should use relative imports when submitting the agent!

    run_a_tournament(NewNegotiator, small=True)
