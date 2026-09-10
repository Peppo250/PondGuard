from dataclasses import dataclass
import math

from .state import PondState


@dataclass
class PondDynamicsConfig:
    """Simple first-order pond model.

    This is NOT a validated aquaculture model. It is a controllable software
    environment for testing controller behavior.
    """
    baseline_do_mg_l: float = 6.5
    natural_oxygen_demand_mg_l_per_h: float = 0.08
    night_oxygen_demand_multiplier: float = 1.8
    aeration_gain_mg_l_per_h: float = 1.5
    nh3_production_mg_l_per_h: float = 0.01
    nh3_aeration_reduction_fraction: float = 0.08
    temperature_effect_per_c: float = 0.015
    ph_effect_per_unit: float = 0.05


class PondModel:
    """Deterministic virtual pond for repeatable controller experiments."""

    def __init__(self, state: PondState, config: PondDynamicsConfig | None = None):
        self.state = state
        self.config = config or PondDynamicsConfig()

    @staticmethod
    def _night(time_min: float) -> bool:
        hour = (time_min / 60.0) % 24.0
        return hour >= 18.0 or hour < 6.0

    def step(self, dt_min: float) -> PondState:
        """Advance the virtual pond by dt_min."""
        c = self.config
        s = self.state

        # Environmental demand is higher at night.
        demand = c.natural_oxygen_demand_mg_l_per_h
        if self._night(s.time_min):
            demand *= c.night_oxygen_demand_multiplier

        # Keep the model easy to reason about: DO falls due to demand and
        # rises when aeration is active.
        temp_factor = max(0.25, 1.0 + (s.temperature_c - 28.0) * c.temperature_effect_per_c)
        ph_factor = max(0.25, 1.0 + (s.ph - 8.0) * c.ph_effect_per_unit)
        demand *= temp_factor * ph_factor

        aeration = c.aeration_gain_mg_l_per_h if s.aerator_on else 0.0
        do_delta_h = aeration - demand
        s.dissolved_oxygen_mg_l += do_delta_h * (dt_min / 60.0)

        # NH3 slowly accumulates; aeration provides only a small indirect effect
        # in this simplified test environment.
        nh3_delta = c.nh3_production_mg_l_per_h * (dt_min / 60.0)
        if s.aerator_on:
            nh3_delta *= (1.0 - c.nh3_aeration_reduction_fraction)
        s.free_nh3_mg_l += nh3_delta

        # Tiny drift around baseline temperature/pH keeps the scenario model
        # deterministic but not completely static.
        s.temperature_c += math.sin(s.time_min / 90.0) * 0.0008 * dt_min
        s.ph += math.sin(s.time_min / 120.0) * 0.0002 * dt_min

        s.dissolved_oxygen_mg_l = max(0.0, min(14.0, s.dissolved_oxygen_mg_l))
        s.free_nh3_mg_l = max(0.0, s.free_nh3_mg_l)
        s.ph = max(4.0, min(11.0, s.ph))

        s.time_min += dt_min
        return s
