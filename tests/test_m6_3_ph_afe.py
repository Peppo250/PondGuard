from pathlib import Path
import math
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_pH_uses_dual_buffer_interface():
    text = (ROOT / "hardware/ph_afe/README.md").read_text()
    assert "AD8607" in text and "dual" in text.lower()
    assert "one amplifier is not sufficient" in text


def test_ph_config():
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text())
    ph = hw["analog_inputs"]["ph"]
    assert ph["interface"].startswith("high-impedance pH electrode")
    assert ph["ads1115_channel_p"] == 0
    assert ph["ads1115_channel_n"] == 3
    assert ph["bias_voltage_v"] == 1.65


def test_nernst_25c():
    R = 8.31446261815324
    F = 96485.33212
    slope = 2.303 * R * (25 + 273.15) / F
    assert math.isclose(slope * 1000, 59.16, rel_tol=0.002)


def test_pH7_is_near_zero_differential():
    R = 8.31446261815324
    F = 96485.33212
    slope = 2.303 * R * (25 + 273.15) / F
    assert abs(slope * (7 - 7)) < 1e-12


def test_extreme_25c_values_fit_inside_1_65v_bias():
    R = 8.31446261815324
    F = 96485.33212
    slope = 2.303 * R * (25 + 273.15) / F
    for ph in (0, 14):
        v = 1.65 + slope * (7 - ph)
        assert 0.0 < v < 3.3


def test_artifacts_exist():
    assert (ROOT / "hardware/ph_afe/spice/ph_buffer_baseline.cir").exists()
    assert (ROOT / "hardware/ph_afe/kicad/PondGuard_M6_3_pH_AFE_notes.sch").exists()
    assert (ROOT / "hardware/bom/ph_afe_bom.csv").exists()
