from dataclasses import dataclass
import random

from simulation.models.state import PondState, SensorReading, SensorSample


@dataclass
class SensorModelConfig:
    do_noise_sd: float = 0.02
    nh3_noise_sd: float = 0.005
    ph_noise_sd: float = 0.01
    temperature_noise_sd: float = 0.03
    failure_probability: float = 0.0
    seed: int = 42


class SensorSimulator:
    """Turn ideal pond state into noisy/faulted virtual sensor readings."""

    def __init__(self, config: SensorModelConfig | None = None):
        self.cfg = config or SensorModelConfig()
        self.rng = random.Random(self.cfg.seed)

    def _reading(self, value: float, sd: float, timestamp: float) -> SensorReading:
        if self.rng.random() < self.cfg.failure_probability:
            return SensorReading(float("nan"), valid=False, timestamp_min=timestamp)
        noisy = value + self.rng.gauss(0.0, sd)
        return SensorReading(noisy, valid=True, noise=noisy - value, timestamp_min=timestamp)

    def read(self, state: PondState) -> SensorSample:
        t = state.time_min
        return SensorSample(
            time_min=t,
            dissolved_oxygen_mg_l=self._reading(state.dissolved_oxygen_mg_l, self.cfg.do_noise_sd, t),
            free_nh3_mg_l=self._reading(state.free_nh3_mg_l, self.cfg.nh3_noise_sd, t),
            ph=self._reading(state.ph, self.cfg.ph_noise_sd, t),
            temperature_c=self._reading(state.temperature_c, self.cfg.temperature_noise_sd, t),
        )
