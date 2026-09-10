import argparse
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from simulation.scenario import load_scenario
from simulation.runner import run_scenario, write_csv


def main():
    parser = argparse.ArgumentParser(description="Run a PondGuard M2 scenario")
    parser.add_argument("scenario", help="Path to scenario JSON")
    parser.add_argument("--output", default="simulation/output.csv")
    args = parser.parse_args()

    scenario = load_scenario(args.scenario)
    records = run_scenario(scenario)

    write_csv(records, args.output)

    aerator_times = [
        r.state.time_min
        for r in records
        if r.aerator_command
    ]
    high_scores = [
        r.crash_score
        for r in records
        if r.crash_score is not None
    ]

    print(f"Scenario: {scenario.name}")
    print(f"Duration: {scenario.duration_min} min")
    print(f"Samples: {len(records)}")
    print(f"Peak crash score: {max(high_scores):.2f}")
    print(f"Aerator active at {len(aerator_times)} samples")
    print(f"CSV: {args.output}")


if __name__ == "__main__":
    main()
