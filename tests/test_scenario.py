from pathlib import Path

from simulation.scenario import load_scenario
from simulation.runner import run_scenario


ROOT = Path(__file__).resolve().parents[1]


def test_normal_day_runs():
    s = load_scenario(ROOT / "simulation/scenarios/normal_day.json")
    records = run_scenario(s)
    assert len(records) > 10
    assert all(r.crash_score is not None for r in records)


def test_night_hypoxia_invokes_aeration():
    s = load_scenario(ROOT / "simulation/scenarios/night_hypoxia.json")
    records = run_scenario(s)
    assert any(r.aerator_command for r in records)


def test_ammonia_spike_is_detected():
    s = load_scenario(ROOT / "simulation/scenarios/ammonia_spike.json")
    records = run_scenario(s)
    scores = [r.crash_score for r in records if r.crash_score is not None]
    assert max(scores) - min(scores) > 10
    assert any(r.state.free_nh3_mg_l >= 0.5 for r in records)


def test_sensor_failure_can_trigger_fail_safe():
    s = load_scenario(ROOT / "simulation/scenarios/sensor_failure.json")
    records = run_scenario(s)
    assert any(r.alert == "FAIL_SAFE_SENSOR_FAULT" for r in records)
