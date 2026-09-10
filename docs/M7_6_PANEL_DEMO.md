# PondGuard — Panel Demo Script

## Live Wokwi demonstration

Open `wokwi/ci/diagram.json` in the Wokwi VS Code extension and start the simulation.

Show the panel:

1. **Normal:** DO knob around 60%. Observe valid telemetry and aerator OFF.
2. **Hypoxia:** drag DO knob to about 20%. Within one sample cycle, observe `DO_LOW` and aerator LED/relay ON.
3. **Recovery:** return DO to about 70%. Observe aerator return OFF.
4. **pH:** move signal/bias pots together to demonstrate the differential pH path.
5. **Battery:** move the battery pot down to trigger the low-battery reason.
6. **Safety:** open the serial monitor and type `TEST SENSOR_FAIL`; observe fail-safe aerator ON. Type `TEST SENSOR_OK` to recover.
7. **Peripheral proof:** `TEST GSM` emits an AT frame on the UART interface; `TEST PUMP` pulses the DO circulation pump.

## Automated evidence

In a separate terminal:

```bash
python tools/run_full_validation.py
```

The command should end with:

```text
FINAL STATUS: PASS
```

Then open:

```text
reports/m7_6/full_validation_report.md
```

and the `wokwi/ci/artifacts/` folder for serial logs and VCD waveforms.

## What to say

> “This is not only a unit-test result. The pipeline compiles the ESP32-C3 firmware, lints the circuit, runs the hardware simulation, injects defined operating conditions, verifies physical GPIO responses, records telemetry, repeats the same scenario, and compares the resulting measurement hash for reproducibility.”
