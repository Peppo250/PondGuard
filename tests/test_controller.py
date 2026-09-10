from simulation.models.controller import ControllerConfig, PondGuardController
from simulation.models.state import PondState


def make_state(do=7.0, nh3=0.05, ph=8.0, temp=28.0, time=600.0):
    return PondState(
        time_min=time,
        dissolved_oxygen_mg_l=do,
        free_nh3_mg_l=nh3,
        ph=ph,
        temperature_c=temp,
    )


def test_low_do_turns_aerator_on():
    c = PondGuardController()
    on, score, reason = c.decide(make_state(do=3.5))
    assert on is True
    assert reason == "DO_LOW"
    assert score >= 0


def test_healthy_state_can_turn_off():
    c = PondGuardController()
    c.aerator_on = True
    state = make_state(do=7.5, nh3=0.03, time=720)
    on, score, reason = c.decide(state)
    assert on is False
    assert reason == "NORMAL"


def test_fail_safe():
    c = PondGuardController()
    on, _, reason = c.decide(make_state(), sensor_valid=False)
    assert on is True
    assert reason == "FAIL_SAFE_SENSOR_FAULT"
