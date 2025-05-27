from anl2025 import anl2025_tournament, make_multideal_scenario
import pathlib
from anl2025.negotiator import Boulware2025, Random2025, Linear2025
from anl2025.scenario import MultidealScenario
from myagent import job_dinner_agent  


generated_scenario = make_multideal_scenario(nedges=3)
path = pathlib.Path("official_test_scenarios/TargetQuantity_example")
scenario = MultidealScenario.from_folder(path)
results = anl2025_tournament(
    scenarios=[scenario],
    n_jobs=-1,
    competitors=(Boulware2025, Linear2025, job_dinner_agent),
    verbose=True,
     no_double_scores=False,
)

print(results.final_scores)
print(results.weighted_average)