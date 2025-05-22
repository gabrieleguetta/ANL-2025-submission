"""
Test script for evaluating the ImprovedUnifiedNegotiator agent on the dinners scenario.
"""
from anl2025 import run_session, MultidealScenario
from anl2025.negotiator import Boulware2025, Linear2025, Random2025
import pathlib

from myagent.job_dinner_agent import ImprovedUnifiedNegotiator

def test_on_dinners_scenario():
    """Test the ImprovedUnifiedNegotiator on the dinners scenario."""
    # Load the dinners scenario
    path = pathlib.Path("")
    scenario = MultidealScenario.from_folder(path)

    print("\n===== Testing ImprovedUnifiedNegotiator as center agent =====")

    # Test against different edge agent combinations
    edge_combinations = [
        [Boulware2025, Boulware2025, Boulware2025],
        [Linear2025, Linear2025, Linear2025],
        [Random2025, Random2025, Random2025],
        [Boulware2025, Linear2025, Random2025]
    ]

    for i, edge_agents in enumerate(edge_combinations):
        print(f"\nTest {i+1}: Against {[agent.__name__ for agent in edge_agents]}")
        results = run_session(
            scenario=scenario,
            center_type=ImprovedUnifiedNegotiator,
            edge_types=edge_agents,
            nsteps=100,
        )
        print(f"Center utility: {results.center_utility}")
        print(f"Edge Utilities: {results.edge_utilities}")
        print(f"Agreements: {results.agreements}")

    print("\n===== Testing ImprovedUnifiedNegotiator as edge agent (all edges are ImprovedUnifiedNegotiator) =====")

    # Test against different center agents
    center_agents = [Boulware2025, Linear2025, Random2025]

    for i, center_agent in enumerate(center_agents):
        print(f"\nTest {i+1}: Against center agent {center_agent.__name__}")
        results = run_session(
            scenario=scenario,
            center_type=center_agent,
            edge_types=[ImprovedUnifiedNegotiator, ImprovedUnifiedNegotiator, ImprovedUnifiedNegotiator],
            nsteps=100,
        )
        print(f"Center utility: {results.center_utility}")
        print(f"Edge Utilities: {results.edge_utilities}")
        print(f"Agreements: {results.agreements}")

    print("\n===== Testing ImprovedUnifiedNegotiator as one of multiple different edge agents =====")

    # Test cases where ImprovedUnifiedNegotiator is mixed with other agent types as edges
    mixed_edge_combinations = [
        [ImprovedUnifiedNegotiator, Boulware2025, Linear2025],
        [ImprovedUnifiedNegotiator, Random2025, Boulware2025],
        [Boulware2025, ImprovedUnifiedNegotiator, Random2025],
        [Linear2025, Random2025, ImprovedUnifiedNegotiator]
    ]

    for i, edge_agents in enumerate(mixed_edge_combinations):
        center_agent = Linear2025 if i % 2 == 0 else Boulware2025
        print(f"\nTest {i+1}: Center: {center_agent.__name__}, Edges: {[agent.__name__ for agent in edge_agents]}")
        results = run_session(
            scenario=scenario,
            center_type=center_agent,
            edge_types=edge_agents,
            nsteps=100,
        )
        print(f"Center utility: {results.center_utility}")
        print(f"Edge Utilities: {results.edge_utilities}")
        print(f"Agreements: {results.agreements}")

        # Identify which edge agent is the ImprovedUnifiedNegotiator and its performance
        for j, agent_type in enumerate(edge_agents):
            if agent_type == ImprovedUnifiedNegotiator:
                print(f"ImprovedUnifiedNegotiator is edge {j} with utility: {results.edge_utilities[j]}")

    print("\n===== Comparing all agents as center against edges Boulware2025, Linear2025, Random2025 =====")

    # Compare all agents in center role
    all_agents = [ImprovedUnifiedNegotiator, Boulware2025, Linear2025, Random2025]

    for center_agent in all_agents:
        # Use a balanced set of opponents
        edge_agents = [Boulware2025, Linear2025, Random2025]
        print(f"\nTest with {center_agent.__name__} as center:")
        results = run_session(
            scenario=scenario,
            center_type=center_agent,
            edge_types=edge_agents,
            nsteps=100,
        )
        print(f"Center utility: {results.center_utility}")
        print(f"Edge Utilities: {results.edge_utilities}")
        print(f"Agreements: {results.agreements}")

if __name__ == "__main__":
    test_on_dinners_scenario()