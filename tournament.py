from anl2025 import anl2025_tournament, make_multideal_scenario
import pathlib
from anl2025.negotiator import Boulware2025, Random2025, Linear2025
from anl2025.scenario import MultidealScenario
from myagent.job_dinner_agent import ImprovedUnifiedNegotiator
from myagent.itay_agent import ItayNegotiator
from myagent.dinners_agent import DinnersNegotiator
from myagent.job_henter_agent import JobHunterNegotiator
# import cProfile

generated_scenario = make_multideal_scenario(nedges=3)
# TargetQuantity_example
# TargetQuantity_example
# job_hunt_target
path1 = pathlib.Path("official_test_scenarios/TargetQuantity_example")
path2 = pathlib.Path("official_test_scenarios/dinners")
path3 = pathlib.Path("official_test_scenarios/job_hunt_target")

scenario1 = MultidealScenario.from_folder(path1)
scenario2 = MultidealScenario.from_folder(path2)
scenario3 = MultidealScenario.from_folder(path3)
results = anl2025_tournament(
    scenarios=[scenario1],
    n_repetitions=10,
    n_jobs=-1,
    competitors=(ItayNegotiator, Boulware2025),
    verbose=True,
     no_double_scores=False,
)

print(results.final_scores)
print(results.weighted_average)