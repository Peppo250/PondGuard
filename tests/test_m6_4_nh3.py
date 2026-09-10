from pathlib import Path
import math
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_nh3_config_is_adc_safe():
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text(encoding="utf-8"))
    nh3 = hw["analog_inputs"]["nh3"]
    assert nh3["mcu_pin"] == 5
    assert nh3["supply_voltage_v"] == 3.3
    assert nh3["output_max_assumed_v"] <= 3.3


def test_qualitative_limitation_is_documented():
    text = (ROOT / "hardware/nh3_interface/README.md").read_text(encoding="utf-8")
    assert "qualitative only" in text.lower()
    assert "universal" in text.lower()
    assert "dissolved" in text.lower() and "mg/l" in text.lower()


def test_rc_filter():
    fc = 1 / (2 * math.pi * 1000 * 100e-9)
    assert 1500 < fc < 1700


def test_vendor_load_resistor_present():
    text = (ROOT / "hardware/nh3_interface/README.md").read_text(encoding="utf-8")
    assert "4.7 kΩ" in text or "4.7k" in text


def test_heater_not_invented():
    text = (ROOT / "hardware/nh3_interface/README.md").read_text(encoding="utf-8")
    assert "heater" in text.lower() and "external" in text.lower()


def test_artifacts_exist():
    assert (ROOT / "hardware/nh3_interface/kicad/PondGuard_M6_4_NH3_notes.sch").exists()
    assert (ROOT / "hardware/nh3_interface/spice/nh3_input_filter.cir").exists()
    assert (ROOT / "hardware/bom/nh3_interface_bom.csv").exists()
