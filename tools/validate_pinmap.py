from pathlib import Path
import json, yaml

ROOT = Path(__file__).resolve().parents[1]
hw = yaml.safe_load((ROOT / "config/hardware.yaml").read_text())
pinmap = json.loads((ROOT / "config/pinmap_m6_5.json").read_text())

assignments = pinmap["assignments"]
gpios = [a["gpio"] for a in assignments]
assert len(gpios) == len(set(gpios)), "duplicate GPIO assignment"

strapping = {2, 8, 9}
assert not strapping.intersection(gpios), "strapping pin assigned"

# Check source-of-truth parity for key interfaces.
assert hw["buses"]["i2c"]["sda"] == 6
assert hw["buses"]["i2c"]["scl"] == 7
assert hw["buses"]["onewire"]["data"] == 4
assert hw["buses"]["spi"]["miso"] == 19
assert hw["buses"]["spi"]["mosi"] == 18
assert hw["buses"]["spi"]["sck"] == 10
assert hw["buses"]["spi"]["cs"] == 3
assert hw["communications"]["gsm"]["tx_pin"] == 21
assert hw["communications"]["gsm"]["rx_pin"] == 20
assert hw["actuators"]["aerator"]["logical_output_pin"] == 0
assert hw["actuators"]["do_circulation_pump"]["logical_output_pin"] == 1

ads = {x["channel"]: x["signal"] for x in pinmap["ads1115"]}
assert ads == {"AIN0": "PH_SIGNAL", "AIN1": "DO_SIGNAL",
               "AIN2": "BATTERY_DIVIDER", "AIN3": "PH_BIAS"}

print("M6.5 pin-map validation: PASS")
