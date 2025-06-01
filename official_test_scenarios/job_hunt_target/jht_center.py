"""
Test script for evaluating the JobHunterNegotiator agent on the job_hunt_target scenario.
"""
from anl2025 import run_session, MultidealScenario
from anl2025.negotiator import Boulware2025, Linear2025, Random2025
import pathlib

from myagent.job_henter_agent import JobHunterNegotiator
from myagent.myagent import NewNegotiator
from myagent.dinners_agent import DinnersNegotiator
from myagent.job_dinner_agent import ImprovedUnifiedNegotiator
from myagent.itay_agent import ItayNegotiator


def run_tour(edge_agents, center_type, scenario, i):
    results = run_session(
        scenario=scenario,
        center_type=center_type,
        edge_types=edge_agents,
        nsteps=10,
    )
    print(f"Center utility: {results.center_utility}")
    print(f"agents: \t\t" + " | ".join(f"{edge.__name__:<20}" for edge in edge_agents))
    print(f"Edge Utilities: \t" + " | ".join(f"{r:<20}" for r in results.edge_utilities))
    print(f"Agreements: \t\t" + " | ".join(f"({','.join(str(sub_a) for sub_a in a) if a != None else 'None'})".ljust(20) for a in results.agreements))



def test_center(edge_combinations, center_type, scenario):
    print(f"\n===== Testing {center_type.__name__} as center agent (employer) =====")
    
    for i, edge_agents in enumerate(edge_combinations):
        print(f"\nTest {i+1}: Against {[agent.__name__ for agent in edge_agents]}")
        run_tour(edge_agents, center_type, scenario, i)

def test_edge(center_agents, edge_combination, scenario):
    for i, center_agent in enumerate(center_agents):
        print(f"\nTest {i+1}: Against center agent {center_agent.__name__}")
        run_tour(edge_combination, center_agent, scenario, i)


def test_on_job_hunt_scenario():
    """Test the ImprovedUnifiedNegotiator on the job_hunt_target scenario."""
    # Load the job_hunt_target scenario
    path = pathlib.Path("official_test_scenarios/dinners")
    path = pathlib.Path("official_test_scenarios/TargetQuantity_example")
    path = pathlib.Path("official_test_scenarios/job_hunt_target")
    scenario = MultidealScenario.from_folder(path)

    # Test against different edge agent combinations
    # The job_hunt_target scenario has 4 edges (employees)
    edge_combinations = [
        #[Boulware2025, Boulware2025, Boulware2025, Boulware2025],
        #[Linear2025, Linear2025, Linear2025, Linear2025],
        #[Random2025, Random2025, Random2025, Random2025],
        #[JobHunterNegotiator, JobHunterNegotiator, JobHunterNegotiator, JobHunterNegotiator],
        [JobHunterNegotiator, ItayNegotiator, DinnersNegotiator, ImprovedUnifiedNegotiator],
        #[DinnersNegotiator, DinnersNegotiator, DinnersNegotiator, DinnersNegotiator],
        #[ImprovedUnifiedNegotiator, ImprovedUnifiedNegotiator, ImprovedUnifiedNegotiator, ImprovedUnifiedNegotiator],
        #[Boulware2025, Linear2025, Random2025, Linear2025]
    ]

    test_center(edge_combinations, ImprovedUnifiedNegotiator, scenario)

    test_center(edge_combinations, JobHunterNegotiator, scenario)
    
    test_center(edge_combinations, ItayNegotiator, scenario)

    print("\n===== Testing NewNegotiator as edge agent (employee) =====")

    # Test against different center agents
    center_agents = [ItayNegotiator, JobHunterNegotiator, DinnersNegotiator, ImprovedUnifiedNegotiator]
    edge_types = [JobHunterNegotiator, ItayNegotiator, ImprovedUnifiedNegotiator, DinnersNegotiator]
    
    test_edge(center_agents, edge_types, scenario)

    print("\n===== Comparing all agents as center (employer) =====")

    # Compare all agents in center role
    all_agents = [NewNegotiator, Boulware2025, JobHunterNegotiator, DinnersNegotiator, ImprovedUnifiedNegotiator]
    edge_agents = [DinnersNegotiator, ImprovedUnifiedNegotiator, JobHunterNegotiator, ItayNegotiator]

    test_edge(all_agents, edge_agents, scenario)

if __name__ == "__main__":
    test_on_job_hunt_scenario()
