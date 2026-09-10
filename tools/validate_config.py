from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main() -> int:
    hw = load_yaml(ROOT / "config/hardware.yaml")
    th = load_yaml(ROOT / "config/thresholds.yaml")
    sim = load_yaml(ROOT / "config/simulation.yaml")

    required_top = ["mcu", "analog_inputs", "digital_sensors", "actuators", "power", "safety"]
    missing = [k for k in required_top if k not in hw]
    if missing:
        print("ERROR: missing hardware sections:", ", ".join(missing))
        return 1

    pins = []
    for section in ("analog_inputs",):
        for _, item in hw[section].items():
            if "mcu_pin" in item:
                pins.append(("analog:" + _, item["mcu_pin"]))

    for _, item in hw["actuators"].items():
        pins.append(("actuator:" + _, item["logical_output_pin"]))

    # Pin collisions are only checked among explicit MCU GPIO assignments.
    values = [p for _, p in pins if p is not None]
    if len(values) != len(set(values)):
        print("ERROR: GPIO collision detected:", pins)
        return 1

    assert th["control"]["aerator"]["on_do_mg_l"] < th["control"]["aerator"]["off_do_mg_l"]
    assert hw["safety"]["aerator_safe_state"] == "ON"
    assert sim["simulation"]["analog"]["do"]["engineering_max"] > sim["simulation"]["analog"]["do"]["engineering_min"]

    print("PondGuard M1 configuration validation: PASS")
    print("GPIO assignments:", pins)
    print("Aerator fail-safe:", hw["safety"]["aerator_safe_state"])
    print("DO control baseline:",
          th["control"]["aerator"]["on_do_mg_l"], "->",
          th["control"]["aerator"]["off_do_mg_l"], "mg/L")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
