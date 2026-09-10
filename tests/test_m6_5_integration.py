from pathlib import Path
import json, yaml

ROOT = Path(__file__).resolve().parents[1]

def test_no_gpio_collision():
    p = json.loads((ROOT / "config/pinmap_m6_5.json").read_text())
    gpios = [x["gpio"] for x in p["assignments"]]
    assert len(gpios) == len(set(gpios))

def test_no_strapping_pins():
    p = json.loads((ROOT / "config/pinmap_m6_5.json").read_text())
    gpios = {x["gpio"] for x in p["assignments"]}
    assert not ({2, 8, 9} & gpios)

def test_ads1115_channel_allocation():
    p = json.loads((ROOT / "config/pinmap_m6_5.json").read_text())
    assert p["ads1115"] == [
        {"channel": "AIN0", "signal": "PH_SIGNAL"},
        {"channel": "AIN1", "signal": "DO_SIGNAL"},
        {"channel": "AIN2", "signal": "BATTERY_DIVIDER"},
        {"channel": "AIN3", "signal": "PH_BIAS"},
    ]

def test_nh3_stays_gpio5():
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text())
    assert hw["analog_inputs"]["nh3"]["mcu_pin"] == 5

def test_gsm_uart_and_safe_power_architecture():
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text())
    assert hw["communications"]["gsm"]["tx_pin"] == 21
    assert hw["communications"]["gsm"]["rx_pin"] == 20
    assert "4.0" in hw["communications"]["gsm"]["power_rail"]

def test_usb_jtag_tradeoff_documented():
    text = (ROOT / "docs/M6_5.md").read_text().lower()
    assert "usb-jtag" in text
    assert "gpio18" in text and "gpio19" in text

def test_aerator_fail_safe_and_driver_stage():
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text())
    assert hw["actuators"]["aerator"]["logical_output_pin"] == 0
    assert hw["actuators"]["aerator"]["fail_safe"] == "ON"
    assert hw["safety"]["relay_outputs_require_driver_stage"] is True

def test_buzzer_removed_to_resolve_conflict():
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text())
    assert hw["status_outputs"]["buzzer"]["pin"] is None
