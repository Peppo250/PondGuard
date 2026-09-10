from pathlib import Path

from simulation.scenario import load_scenario
from simulation.runner import run_scenario


ROOT = Path(__file__).resolve().parents[1]


def signature(records):
    return [
        (
            round(r.state.time_min, 4),
            round(r.state.dissolved_oxygen_mg_l, 4),
            round(r.crash_score or 0.0, 4),
            bool(r.aerator_command),
            r.alert,
        )
        for r in records
    ]


def test_same_seed_is_repeatable():
    s = load_scenario(ROOT / "simulation/scenarios/night_hypoxia.json")
    a = run_scenario(s)
    b = run_scenario(s)
    assert signature(a) == signature(b)
