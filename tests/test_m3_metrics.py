from simulation.evaluation.metrics import evaluate_records
from simulation.models.state import PondState, SimulationRecord


def record(t, do, score, aerator, alert=None):
    state = PondState(
        time_min=t,
        dissolved_oxygen_mg_l=do,
        free_nh3_mg_l=0.1,
        ph=8.0,
        temperature_c=28.0,
        aerator_on=aerator,
    )
    return SimulationRecord(
        state=state,
        crash_score=score,
        aerator_command=aerator,
        alert=alert,
    )


def test_detects_crash():
    records = [
        record(0, 6.0, 10, False),
        record(5, 3.8, 75, True),
    ]
    r = evaluate_records("x", records)
    assert r.crash_event is True
    assert r.detected is True
    assert r.missed_event is False
    assert r.time_to_detection_min == 0


def test_detects_missed_crash():
    records = [
        record(0, 6.0, 10, False),
        record(5, 3.5, 60, False),
    ]
    r = evaluate_records("x", records)
    assert r.missed_event is True


def test_false_activation():
    records = [
        record(0, 7.0, 10, True),
        record(5, 7.0, 10, False),
    ]
    r = evaluate_records("x", records)
    assert r.false_activation is True


def test_early_detection_has_positive_lead_time():
    records = [
        record(0, 6.0, 10, True),
        record(5, 3.8, 75, True),
    ]
    r = evaluate_records("early", records)
    assert r.time_to_detection_min == -5
    assert r.detection_lead_time_min == 5
