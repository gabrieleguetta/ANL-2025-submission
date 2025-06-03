from anl2025 import anl2025_tournament, make_multideal_scenario
from anl2025.negotiator import Boulware2025, Random2025, Linear2025
from anl2025.scenario import MultidealScenario
import pathlib
from myagent.job_henter_agent import JobHunterNegotiator
from myagent.myagent import NewNegotiator
from myagent.dinners_agent import DinnersNegotiator
from myagent.job_dinner_agent import ImprovedUnifiedNegotiator
from myagent.itay_agent import ItayNegotiator


def run_tour(path, agent):
    print(f"\n\n\nscenario {path}\n\n\n")
    scenario = MultidealScenario.from_folder(path)
    generated_scenario = make_multideal_scenario(nedges=3)
    results = anl2025_tournament(
        scenarios=[scenario, generated_scenario],
        n_jobs=-1,
        competitors=(agent, Boulware2025, Linear2025),
        verbose=True,
        #  no_double_scores=False,
    )

    print(results.final_scores)
    print(results.weighted_average)


def test_agents(scenario):
    agents = [
          ItayNegotiator,
          ImprovedUnifiedNegotiator, 
          DinnersNegotiator, 
          NewNegotiator
          ]
    for a in agents:
        print(a.__name__)
        run_tour(scenario, a)


def run_tournaments():
    path = pathlib.Path("official_test_scenarios/dinners")
    test_agents(path)
    path = pathlib.Path("official_test_scenarios/TargetQuantity_example")
    test_agents(path)
    path = pathlib.Path("official_test_scenarios/job_hunt_target")
    test_agents(path)



if __name__ == "__main__":
    run_tournaments()
