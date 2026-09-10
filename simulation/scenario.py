from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class Event:
    time_min: float
    field: str
    value: float


@dataclass
class Scenario:
    name: str
    duration_min: float
    timestep_min: float
    initial: dict
    events: list[Event] = field(default_factory=list)
    sensor_config: dict = field(default_factory=dict)
    pond_config: dict = field(default_factory=dict)


def load_scenario(path: str | Path) -> Scenario:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    events = [Event(**e) for e in data.get("events", [])]
    return Scenario(
        name=data["name"],
        duration_min=data["duration_min"],
        timestep_min=data.get("timestep_min", 5.0),
        initial=data["initial"],
        events=events,
        sensor_config=data.get("sensor_config", {}),
        pond_config=data.get("pond_config", {}),
    )
