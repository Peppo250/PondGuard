from dataclasses import dataclass
from collections import deque
import math

from .state import PondState


@dataclass
class ControllerConfig:
    do_warning_mg_l: float = 5.5
    do_aerator_on_mg_l: float = 4.0
    do_aerator_off_mg_l: float = 5.5
    nh3_alarm_mg_l: float = 0.5

    # Proposed baseline weights from the project simulation.
    w_do: float = 0.38
    w_trend: float = 0.22
    w_nh3: float = 0.25
    w_temperature: float = 0.05
    w_time: float = 0.10

    trend_window_min: float = 15.0
    high_risk_score: float = 70.0
    low_risk_score: float = 45.0

    battery_low_v: float = 6.8


class PondGuardController:
    """Reference controller for software experiments.

    Important:
    - This is a proposed baseline, not a validated control law.
    - No ML is used in M2.
    - The controller is deliberately deterministic and explainable.
    """

    def __init__(self, config: ControllerConfig | None = None):
        self.cfg = config or ControllerConfig()
        self.aerator_on = False
        self.history = deque(maxlen=64)

    @staticmethod
    def _clamp01(x: float) -> float:
        return max(0.0, min(1.0, x))

    def _night_risk(self, time_min: float) -> float:
        hour = (time_min / 60.0) % 24.0
        return 1.0 if (hour >= 18.0 or hour < 6.0) else 0.25

    def _trend(self, state: PondState) -> float:
        self.history.append((state.time_min, state.dissolved_oxygen_mg_l))
        if len(self.history) < 2:
            return 0.0

        target_t = state.time_min - self.cfg.trend_window_min
        old = None
        for t, do in self.history:
            if t <= target_t:
                old = (t, do)
            else:
                break

        if old is None:
            t0, do0 = self.history[0]
        else:
            t0, do0 = old

        dt = max(1e-6, state.time_min - t0)
        return (state.dissolved_oxygen_mg_l - do0) / dt

    def crash_score(self, state: PondState) -> float:
        dodt = self._trend(state)

        do_risk = self._clamp01((self.cfg.do_warning_mg_l - state.dissolved_oxygen_mg_l) / 2.0)
        trend_risk = self._clamp01((-dodt) / 0.30)
        nh3_risk = self._clamp01(state.free_nh3_mg_l / self.cfg.nh3_alarm_mg_l)
        temp_risk = self._clamp01((state.temperature_c - 30.0) / 5.0)
        time_risk = self._night_risk(state.time_min)

        score = 100.0 * (
            self.cfg.w_do * do_risk
            + self.cfg.w_trend * trend_risk
            + self.cfg.w_nh3 * nh3_risk
            + self.cfg.w_temperature * temp_risk
            + self.cfg.w_time * time_risk
        )
        return max(0.0, min(100.0, score))

    def decide(self, state: PondState, sensor_valid: bool = True) -> tuple[bool, float, str]:
        score = self.crash_score(state)

        if not sensor_valid or not math.isfinite(score):
            self.aerator_on = True
            return True, score, "FAIL_SAFE_SENSOR_FAULT"

        if state.dissolved_oxygen_mg_l < self.cfg.do_aerator_on_mg_l:
            self.aerator_on = True
            return True, score, "DO_LOW"

        if state.free_nh3_mg_l >= self.cfg.nh3_alarm_mg_l and score >= self.cfg.high_risk_score:
            self.aerator_on = True
            return True, score, "HIGH_COMBINED_RISK"

        if score >= self.cfg.high_risk_score:
            self.aerator_on = True
            return True, score, "CRASH_SCORE_HIGH"

        if (
            state.dissolved_oxygen_mg_l > self.cfg.do_aerator_off_mg_l
            and score < self.cfg.low_risk_score
        ):
            self.aerator_on = False
            return False, score, "NORMAL"

        return self.aerator_on, score, "HYSTERESIS_HOLD"
