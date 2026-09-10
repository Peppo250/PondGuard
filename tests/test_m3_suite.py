from pathlib import Path

from simulation.evaluation.suite import evaluate_scenarios, summarize
from simulation.generation.scenarios import generate_scenarios
from simulation.scenario import load_scenario


def test_evaluation_suite_runs(tmp_path):
    generate_scenarios(12, seed=123, output_dir=tmp_path)
    scenarios = [
        load_scenario(p) for p in sorted(tmp_path.glob("*.json"))
    ]
    results = evaluate_scenarios(scenarios)
    summary = summarize(results)

    assert summary["scenarios"] == 12
    assert "crash_detection_rate_pct" in summary
    assert "false_activation_rate_pct" in summary
