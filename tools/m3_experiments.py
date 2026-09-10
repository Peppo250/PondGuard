import argparse
import json
from pathlib import Path
import sys
from dataclasses import asdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from simulation.generation.scenarios import generate_scenarios
from simulation.scenario import load_scenario
from simulation.evaluation.suite import evaluate_scenarios, summarize, write_results_csv


def main():
    parser = argparse.ArgumentParser(description="PondGuard M3 experiment runner")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--out", default="reports/m3")
    args = parser.parse_args()

    out = Path(args.out)
    scenario_dir = out / "scenarios"
    scenario_specs = generate_scenarios(args.count, args.seed, scenario_dir)

    scenarios = [
        load_scenario(scenario_dir / f"{s.name}.json")
        for s in scenario_specs
    ]

    results = evaluate_scenarios(scenarios)
    summary = summarize(results)

    out.mkdir(parents=True, exist_ok=True)
    write_results_csv(results, out / "results.csv")
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )

    print("=== PondGuard M3 Experiment Suite ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print(f"results: {out / 'results.csv'}")
    print(f"summary: {out / 'summary.json'}")


if __name__ == "__main__":
    main()
