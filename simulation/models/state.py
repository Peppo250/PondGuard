from dataclasses import dataclass, field


@dataclass
class PondState:
    """Environmental state used by the M2 virtual pond."""
    time_min: float
    dissolved_oxygen_mg_l: float
    free_nh3_mg_l: float
    ph: float
    temperature_c: float
    aerator_on: bool = False


@dataclass
class SensorReading:
    value: float
    valid: bool = True
    noise: float = 0.0
    timestamp_min: float = 0.0


@dataclass
class SensorSample:
    time_min: float
    dissolved_oxygen_mg_l: SensorReading
    free_nh3_mg_l: SensorReading
    ph: SensorReading
    temperature_c: SensorReading


@dataclass
class SimulationRecord:
    state: PondState
    sample: SensorSample | None = None
    crash_score: float | None = None
    aerator_command: bool | None = None
    alert: str | None = None
