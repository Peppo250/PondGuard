import csv
import math
from pathlib import Path

from simulation.models.state import PondState, SimulationRecord
from simulation.models.pond import PondDynamicsConfig, PondModel
from simulation.models.controller import ControllerConfig, PondGuardController
from simulation.sensors import SensorModelConfig, SensorSimulator
from simulation.scenario import Scenario


def _apply_events(state: PondState, scenario: Scenario, current_time: float, applied: set[int]) -> None:
    for idx, event in enumerate(scenario.events):
        if idx in applied:
            continue
        if current_time >= event.time_min:
            if not hasattr(state, event.field):
                raise ValueError(f"Unknown scenario field: {event.field}")
            setattr(state, event.field, event.value)
            applied.add(idx)


def _sample_to_dict(record: SimulationRecord) -> dict:
    s = record.state
    m = record.sample
    return {
        "time_min": round(s.time_min, 3),
        "true_do_mg_l": round(s.dissolved_oxygen_mg_l, 5),
        "sensor_do_mg_l": round(m.dissolved_oxygen_mg_l.value, 5) if m else "",
        "true_nh3_mg_l": round(s.free_nh3_mg_l, 5),
        "sensor_nh3_mg_l": round(m.free_nh3_mg_l.value, 5) if m else "",
        "sensor_ph": round(m.ph.value, 5) if m else "",
        "sensor_temperature_c": round(m.temperature_c.value, 5) if m else "",
        "crash_score": round(record.crash_score, 5) if record.crash_score is not None else "",
        "aerator": int(bool(record.aerator_command)),
        "alert": record.alert or "",
    }


def run_scenario(
    scenario: Scenario,
    controller_config: ControllerConfig | None = None,
) -> list[SimulationRecord]:
    state = PondState(
        time_min=0.0,
        dissolved_oxygen_mg_l=float(scenario.initial["dissolved_oxygen_mg_l"]),
        free_nh3_mg_l=float(scenario.initial["free_nh3_mg_l"]),
        ph=float(scenario.initial["ph"]),
        temperature_c=float(scenario.initial["temperature_c"]),
        aerator_on=False,
    )

    pond_cfg = PondDynamicsConfig(**scenario.pond_config)
    sensor_cfg = SensorModelConfig(**scenario.sensor_config)

    pond = PondModel(state, pond_cfg)
    sensors = SensorSimulator(sensor_cfg)
    controller = PondGuardController(controller_config)

    records: list[SimulationRecord] = []
    applied: set[int] = set()

    # Sample at t=0, then advance.
    while state.time_min <= scenario.duration_min + 1e-9:
        _apply_events(state, scenario, state.time_min, applied)

        sample = sensors.read(state)
        valid = all(
            r.valid and math.isfinite(r.value)
            for r in [
                sample.dissolved_oxygen_mg_l,
                sample.free_nh3_mg_l,
                sample.ph,
                sample.temperature_c,
            ]
        )

        # Feed sensor measurements into the controller state copy so the
        # controller is driven by virtual sensor observations, not ground truth.
        observed = PondState(
            time_min=sample.time_min,
            dissolved_oxygen_mg_l=sample.dissolved_oxygen_mg_l.value,
            free_nh3_mg_l=sample.free_nh3_mg_l.value,
            ph=sample.ph.value,
            temperature_c=sample.temperature_c.value,
            aerator_on=state.aerator_on,
        )

        aerator, score, reason = controller.decide(observed, sensor_valid=valid)
        state.aerator_on = aerator

        records.append(
            SimulationRecord(
                state=PondState(**vars(state)),
                sample=sample,
                crash_score=score,
                aerator_command=aerator,
                alert=reason if reason != "NORMAL" else None,
            )
        )

        pond.step(scenario.timestep_min)

    return records


def write_csv(records: list[SimulationRecord], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    rows = [_sample_to_dict(r) for r in records]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
