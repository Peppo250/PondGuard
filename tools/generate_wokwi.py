from pathlib import Path
import yaml
import json
import re

ROOT = Path(__file__).resolve().parents[1]
HW = yaml.safe_load((ROOT / "config/hardware.yaml").read_text(encoding="utf-8"))

# Only substitute values that are explicitly represented in the Wokwi harness.
replacements = {
    "PIN_DO_ADC": HW["analog_inputs"]["do"]["mcu_pin"],
    "PIN_NH3_ADC": HW["analog_inputs"]["nh3"]["mcu_pin"],
    "PIN_BATTERY_ADC": HW["analog_inputs"]["battery"]["mcu_pin"],
    "PIN_TEMPERATURE": HW["digital_sensors"]["temperature"]["pin"],
    "PIN_AERATOR_RELAY": HW["actuators"]["aerator"]["logical_output_pin"],
    "PIN_DO_PUMP_RELAY": HW["actuators"]["do_circulation_pump"]["logical_output_pin"],
}

src = ROOT / "wokwi/generated/sketch.ino"
text = src.read_text(encoding="utf-8")

for key, value in replacements.items():
    # Keep the generated harness visibly traceable to config.
    text = re.sub(
        rf"(constexpr int {key}\s*=\s*)\d+;",
        rf"\g<1>{value};",
        text,
    )

src.write_text(text, encoding="utf-8")

print("Wokwi harness regenerated from config/hardware.yaml")
for k, v in replacements.items():
    print(f"  {k} = {v}")
