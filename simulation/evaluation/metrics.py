from dataclasses import dataclass
from typing import Iterable

from simulation.models.state import SimulationRecord


@dataclass
class EvaluationResult:
    scenario_name: str
    crash_event: bool
    detected: bool
    false_activation: bool
    missed_event: bool
    time_to_detection_min: float | None
    detection_lead_time_min: float | None
    min_do_mg_l: float
    peak_crash_score: float
    aerator_samples: int
    total_samples: int
    fail_safe_activation: bool


def _crash_event(records: list[SimulationRecord], threshold: float = 4.0) -> bool:
    return any(r.state.dissolved_oxygen_mg_l < threshold for r in records)


def _first_threshold_time(records: list[SimulationRecord], threshold: float = 4.0):
    for r in records:
        if r.state.dissolved_oxygen_mg_l < threshold:
            return r.state.time_min
    return None


def _first_aerator_time(records: list[SimulationRecord]):
    for r in records:
        if r.aerator_command:
            return r.state.time_min
    return None


def evaluate_records(
    scenario_name: str,
    records: Iterable[SimulationRecord],
    do_crash_threshold: float = 4.0,
) -> EvaluationResult:
    records = list(records)

    event = _crash_event(records, do_crash_threshold)
    crash_time = _first_threshold_time(records, do_crash_threshold)
    aerator_time = _first_aerator_time(records)

    detected = aerator_time is not None
    missed = event and not detected

    # A false activation means the controller activated the aerator in a
    # scenario that never crossed the environmental crash definition.
    false_activation = (not event) and detected

    ttd = None
    lead = None
    if crash_time is not None and aerator_time is not None:
        ttd = aerator_time - crash_time
        # Positive lead time means the controller activated BEFORE the crash threshold.
        lead = crash_time - aerator_time

    min_do = min(r.state.dissolved_oxygen_mg_l for r in records)
    peak_score = max(r.crash_score for r in records if r.crash_score is not None)
    aerator_samples = sum(bool(r.aerator_command) for r in records)
    fail_safe = any(r.alert == "FAIL_SAFE_SENSOR_FAULT" for r in records)

    return EvaluationResult(
        scenario_name=scenario_name,
        crash_event=event,
        detected=detected,
        false_activation=false_activation,
        missed_event=missed,
        time_to_detection_min=ttd,
        detection_lead_time_min=lead,
        min_do_mg_l=min_do,
        peak_crash_score=peak_score,
        aerator_samples=aerator_samples,
        total_samples=len(records),
        fail_safe_activation=fail_safe,
    )
