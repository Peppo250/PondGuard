from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    with open(ROOT / "config" / name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def test_required_files():
    for name in ["hardware.yaml", "thresholds.yaml", "simulation.yaml"]:
        assert (ROOT / "config" / name).exists()

def test_required_pins_are_present_and_unique_for_outputs():
    hw = load("hardware.yaml")
    pins = hw["mcu"]
    assert pins["board"] == "ESP32-C3"

    analog = hw["analog_inputs"]
    assert analog["do"]["mcu_pin"] is None
    assert analog["do"]["ads1115_channel"] == 1
    assert analog["nh3"]["mcu_pin"] == 5
    assert analog["battery"]["mcu_pin"] is None
    assert analog["battery"]["ads1115_channel"] == 2

    outputs = [
        hw["actuators"]["aerator"]["logical_output_pin"],
        hw["actuators"]["do_circulation_pump"]["logical_output_pin"],
    ]
    assert len(outputs) == len(set(outputs))

def test_aerator_fail_safe_is_on():
    hw = load("hardware.yaml")
    assert hw["safety"]["aerator_safe_state"] == "ON"
    assert hw["actuators"]["aerator"]["fail_safe"] == "ON"

def test_proposed_control_values():
    th = load("thresholds.yaml")
    assert th["control"]["aerator"]["on_do_mg_l"] < th["control"]["aerator"]["off_do_mg_l"]
    assert th["control"]["ammonia"]["alarm_free_nh3_mg_l"] > 0
