from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_wokwi_files_exist():
    assert (ROOT / "wokwi/generated/diagram.json").exists()
    assert (ROOT / "wokwi/generated/sketch.ino").exists()
    assert (ROOT / "wokwi/generated/libraries.txt").exists()
    assert (ROOT / "wokwi/generated/ads1115.chip.c").exists()


def test_wokwi_json_is_valid():
    data = json.loads((ROOT / "wokwi/generated/diagram.json").read_text())
    assert data["version"] == 1
    assert any(p["type"] == "board-esp32-c3-devkitm-1" for p in data["parts"])


def test_required_mcu_outputs_are_present():
    data = json.loads((ROOT / "wokwi/generated/diagram.json").read_text())
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text())
    text = (ROOT / "wokwi/generated/sketch.ino").read_text()
    assert hw["actuators"]["aerator"]["logical_output_pin"] == 0
    assert hw["actuators"]["do_circulation_pump"]["logical_output_pin"] == 1
    assert 'constexpr int AERATOR_PIN = 0;' in text
    assert 'constexpr int DO_PUMP_PIN = 1;' in text
    assert any(p["id"] == "aeratorRelay" for p in data["parts"])
    assert any(p["id"] == "pumpRelay" for p in data["parts"])


def test_harness_contains_safety_startup():
    text = (ROOT / "wokwi/generated/sketch.ino").read_text()
    assert "Safety invariant: aerator ON" in text
    assert "digitalWrite(AERATOR_PIN, HIGH);" in text
    assert "digitalWrite(DO_PUMP_PIN, LOW);" in text


def test_wokwi_has_expected_m7_1_peripherals():
    data = json.loads((ROOT / "wokwi/generated/diagram.json").read_text())
    types = [p["type"] for p in data["parts"]]
    assert "board-esp32-c3-devkitm-1" in types
    assert "chip-ads1115" in types
    assert "wokwi-ds18b20" in types
    assert "wokwi-microsd-card" in types
    assert types.count("wokwi-relay-module") == 2
    assert types.count("wokwi-potentiometer") == 5
    assert "wokwi-logic-analyzer" in types
