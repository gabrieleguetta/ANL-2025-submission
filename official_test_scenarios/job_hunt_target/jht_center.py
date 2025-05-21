"""
Test script for evaluating the JobHunterNegotiator agent on the job_hunt_target scenario.
"""
from anl2025 import run_session, MultidealScenario
from anl2025.negotiator import Boulware2025, Linear2025, Random2025
import pathlib

from myagent.job_henter_agent import JobHunterNegotiator
from myagent.myagent import NewNegotiator


def test_on_job_hunt_scenario():
    """Test the NewNegotiator on the job_hunt_target scenario."""
    # Load the job_hunt_target scenario
    path = pathlib.Path("official_test_scenarios/job_hunt_target")
    scenario = MultidealScenario.from_folder(path)

    print("\n===== Testing NewNegotiator as center agent (employer) =====")

    # Test against different edge agent combinations
    # The job_hunt_target scenario has 4 edges (employees)
    edge_combinations = [
        [Boulware2025, Boulware2025, Boulware2025, Boulware2025],
        [Linear2025, Linear2025, Linear2025, Linear2025],
        [Random2025, Random2025, Random2025, Random2025],
        [Boulware2025, Linear2025, Random2025, Linear2025]
    ]

    for i, edge_agents in enumerate(edge_combinations):
        print(f"\nTest {i+1}: Against {[agent.__name__ for agent in edge_agents]}")
        results = run_session(
            scenario=scenario,
            center_type=NewNegotiator,
            edge_types=edge_agents,
            nsteps=10,
        )
        print(f"Center utility: {results.center_utility}")
        print(f"Edge Utilities: {results.edge_utilities}")
        print(f"Agreements: {results.agreements}")

    print("\n===== Testing NewNegotiator as edge agent (employee) =====")

    # Test against different center agents
    center_agents = [Boulware2025, Linear2025, Random2025]

    for i, center_agent in enumerate(center_agents):
        print(f"\nTest {i+1}: Against center agent {center_agent.__name__}")
        # Place NewNegotiator as the first edge agent, with a mix of other agents
        results = run_session(
            scenario=scenario,
            center_type=center_agent,
            edge_types=[NewNegotiator, Boulware2025, Linear2025, Random2025],
            nsteps=10,
        )
        print(f"Center utility: {results.center_utility}")
        print(f"Edge Utilities: {results.edge_utilities}")
        print(f"Agreements: {results.agreements}")
        print(f"NewNegotiator is edge 0 with utility: {results.edge_utilities[0]}")

    print("\n===== Comparing all agents as center (employer) =====")

    # Compare all agents in center role
    all_agents = [NewNegotiator, Boulware2025, Linear2025, Random2025]
    edge_agents = [Boulware2025, Linear2025, Random2025, Linear2025]

    for center_agent in all_agents:
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
    test_on_job_hunt_scenario()
