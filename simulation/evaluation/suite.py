from dataclasses import asdict
from pathlib import Path
import csv

from simulation.models.controller import ControllerConfig
from simulation.runner import run_scenario
from simulation.scenario import Scenario
from simulation.evaluation.metrics import EvaluationResult, evaluate_records


def evaluate_scenarios(
    scenarios: list[Scenario],
    controller_config: ControllerConfig | None = None,
) -> list[EvaluationResult]:
    results = []
    for scenario in scenarios:
        records = run_scenario(scenario, controller_config)
        results.append(evaluate_records(scenario.name, records))
    return results


def summarize(results: list[EvaluationResult]) -> dict:
    n = len(results)
    if n == 0:
        return {
            "scenarios": 0,
            "crash_events": 0,
            "detected": 0,
            "missed": 0,
            "false_activations": 0,
        }

    crash = [r for r in results if r.crash_event]
    detected = [r for r in crash if r.detected]
    missed = [r for r in crash if r.missed_event]
    false = [r for r in results if r.false_activation]
    fail_safe = [r for r in results if r.fail_safe_activation]

    ttd_values = [r.time_to_detection_min for r in detected if r.time_to_detection_min is not None]
    lead_values = [r.detection_lead_time_min for r in detected if r.detection_lead_time_min is not None]

    return {
        "scenarios": n,
        "crash_events": len(crash),
        "detected_crashes": len(detected),
        "missed_crashes": len(missed),
        "false_activations": len(false),
        "fail_safe_activations": len(fail_safe),
        "crash_detection_rate_pct": round((len(detected) / len(crash) * 100) if crash else 0.0, 2),
        "false_activation_rate_pct": round(len(false) / n * 100, 2),
        "mean_detection_time_min": round(sum(ttd_values) / len(ttd_values), 2) if ttd_values else None,
        "mean_detection_lead_time_min": round(sum(lead_values) / len(lead_values), 2) if lead_values else None,
        "worst_min_do_mg_l": round(min(r.min_do_mg_l for r in results), 3),
        "max_crash_score": round(max(r.peak_crash_score for r in results), 3),
    }


def write_results_csv(results: list[EvaluationResult], path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [asdict(r) for r in results]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
