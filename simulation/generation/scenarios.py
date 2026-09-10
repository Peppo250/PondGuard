from dataclasses import dataclass, asdict
from pathlib import Path
import json
import random


@dataclass
class ScenarioSpec:
    name: str
    duration_min: float
    timestep_min: float
    initial: dict
    events: list
    sensor_config: dict


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def generate_scenarios(
    count: int,
    seed: int = 1234,
    output_dir: str | Path | None = None,
) -> list[ScenarioSpec]:
    """Generate reproducible synthetic stress/normal scenarios.

    These scenarios are for software evaluation, not claims about real pond
    dynamics.
    """
    rng = random.Random(seed)
    scenarios: list[ScenarioSpec] = []

    for i in range(count):
        start_do = rng.uniform(4.2, 8.0)
        start_nh3 = rng.uniform(0.02, 0.18)
        ph = rng.uniform(7.2, 8.8)
        temp = rng.uniform(25.0, 33.0)
        duration = rng.choice([360, 540, 720])
        sensor_noise = rng.choice([0.01, 0.02, 0.04, 0.08])
        failure_prob = rng.choice([0.0, 0.0, 0.0, 0.03, 0.10])

        events = []

        # About half are stress scenarios.
        if rng.random() < 0.55:
            t = rng.uniform(240, duration - 30)
            crash_do = rng.uniform(2.8, 4.2)
            crash_nh3 = rng.uniform(0.25, 0.75)
            events.extend([
                {"time_min": round(t, 2), "field": "dissolved_oxygen_mg_l", "value": round(crash_do, 3)},
                {"time_min": round(t, 2), "field": "free_nh3_mg_l", "value": round(crash_nh3, 3)},
            ])

        scenarios.append(
            ScenarioSpec(
                name=f"generated_{i:04d}",
                duration_min=duration,
                timestep_min=5,
                initial={
                    "dissolved_oxygen_mg_l": round(start_do, 3),
                    "free_nh3_mg_l": round(start_nh3, 3),
                    "ph": round(ph, 3),
                    "temperature_c": round(temp, 3),
                },
                events=events,
                sensor_config={
                    "do_noise_sd": sensor_noise,
                    "nh3_noise_sd": sensor_noise / 5,
                    "ph_noise_sd": sensor_noise / 2,
                    "temperature_noise_sd": 0.03,
                    "failure_probability": failure_prob,
                    "seed": seed + i,
                },
            )
        )

    if output_dir is not None:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        for spec in scenarios:
            (out / f"{spec.name}.json").write_text(
                json.dumps(asdict(spec), indent=2) + "\n",
                encoding="utf-8",
            )

    return scenarios
