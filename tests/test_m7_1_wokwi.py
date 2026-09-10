from pathlib import Path
import json
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
WOKWI = ROOT / "wokwi/generated"


def load_diagram():
    return json.loads((WOKWI / "diagram.json").read_text(encoding="utf-8"))


def test_m7_1_wokwi_files_exist():
    for name in ["diagram.json", "sketch.ino", "libraries.txt", "ads1115.chip.json", "ads1115.chip.c"]:
        assert (WOKWI / name).exists()


def test_m7_1_uses_m6_7_pins():
    hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text(encoding="utf-8"))
    d = load_diagram()
    wires = {pair for c in d["connections"] for pair in [(c[0], c[1]), (c[1], c[0])]}
    expected = {
        ("esp:0", "aeratorRelay:IN"),
        ("esp:1", "pumpRelay:IN"),
        ("esp:3", "sd:CS"),
        ("esp:4", "ds:DQ"),
        ("esp:5", "nh3Pot:SIG"),
        ("esp:6", "ads:SDA"),
        ("esp:7", "ads:SCL"),
        ("esp:10", "sd:CLK"),
        ("esp:18", "sd:DI"),
        ("esp:19", "sd:DO"),
        ("esp:20", "logic:D7"),
        ("esp:21", "logic:D6"),
        ("ads:A0", "phSignalPot:SIG"),
        ("ads:A1", "doPot:SIG"),
        ("ads:A2", "batteryPot:SIG"),
        ("ads:A3", "phBiasPot:SIG"),
    }
    assert expected <= wires


def test_no_legacy_m5_direct_adc_assignments():
    text = (WOKWI / "sketch.ino").read_text(encoding="utf-8")
    assert "analogRead(config::DO_ANALOG_PIN)" not in text
    assert "analogRead(config::PH_ANALOG_PIN)" not in text
    assert "analogRead(config::BATTERY_ANALOG_PIN)" not in text
    assert "GPIO 8" not in text
    assert "const int SD_CS = 2" not in text


def test_ads1115_model_has_expected_address_and_channels():
    text = (WOKWI / "ads1115.chip.c").read_text(encoding="utf-8")
    assert '.address = 0x48' in text
    assert 'pin_init("A0", ANALOG)' in text
    assert 'pin_init("A3", ANALOG)' in text


def test_gsm_and_logic_analyzer_present():
    d = load_diagram()
    types = [p["type"] for p in d["parts"]]
    assert "wokwi-logic-analyzer" in types
    sketch = (WOKWI / "sketch.ino").read_text(encoding="utf-8")
    assert "gsm.begin(9600, SERIAL_8N1, GSM_RX, GSM_TX)" in sketch
    assert 'gsm.print("AT\\r\\n")' in sketch


def test_safety_startup_and_relay_polarity():
    text = (WOKWI / "sketch.ino").read_text(encoding="utf-8")
    assert "digitalWrite(AERATOR_PIN, HIGH);" in text
    assert "digitalWrite(DO_PUMP_PIN, LOW);" in text
    d = load_diagram()
    relays = {p["id"]: p for p in d["parts"] if p["type"] == "wokwi-relay-module"}
    assert relays["aeratorRelay"]["attrs"]["transistor"] == "pnp"
    assert relays["pumpRelay"]["attrs"]["transistor"] == "pnp"


def test_no_buzzer_pin_and_strapping_pins_unassigned():
    text = (WOKWI / "sketch.ino").read_text(encoding="utf-8")
    for pin in [2, 8, 9, 12, 13, 14, 15, 16, 17]:
        assert not re.search(rf'\b(pin|GPIO|esp:){pin}\b', text)
