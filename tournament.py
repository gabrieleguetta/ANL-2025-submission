from anl2025 import anl2025_tournament, make_multideal_scenario
import pathlib
from anl2025.negotiator import Boulware2025, Random2025, Linear2025
from anl2025.scenario import MultidealScenario
from myagent.job_dinner_agent import ImprovedUnifiedNegotiator
from myagent.itay_agent import ItayNegotiator
from myagent.dinners_agent import DinnersNegotiator
from myagent.job_henter_agent import JobHunterNegotiator

generated_scenario = make_multideal_scenario(nedges=3)
path = pathlib.Path("new_test_scenarios/supply_chain")
scenario = MultidealScenario.from_folder(path)
results = anl2025_tournament(
    scenarios=[scenario],
    n_jobs=-1,
    competitors=(Boulware2025, Linear2025, JobHunterNegotiator, DinnersNegotiator, ImprovedUnifiedNegotiator, ItayNegotiator),
    verbose=True,
     no_double_scores=False,
)

print(results.final_scores)
print(results.weighted_average)