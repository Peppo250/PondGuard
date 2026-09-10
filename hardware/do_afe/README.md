# PondGuard M6.2 — Dissolved Oxygen Analog Front-End

## Important integration finding

The selected DFRobot SEN0237-A is a complete analog DO kit: a galvanic probe
plus a signal-conditioner board. DFRobot specifies the probe for 0–20 mg/L and
the signal-conditioner output as 0–3.0 V.

Therefore the project must distinguish two alternative electrical branches.

## Branch A — first physical prototype (recommended)

```text
SEN0237-A galvanic probe
          ↓
DFRobot signal conditioner
          ↓
       0–3.0 V
          ↓
       ADS1115
          ↓
       ESP32-C3
```

Do not add the custom current TIA after the vendor-conditioned 0–3 V output.

## Branch B — custom research AFE

```text
bare galvanic DO probe
          ↓
      LM358B TIA
          ↓
   compensation/filter
          ↓
       ADS1115
          ↓
       ESP32-C3
```

Branch B is only for a raw/bare electrochemical probe.

## Existing project baseline

The project design baseline specified approximately 1–3 µA probe current,
Rf = 47 kΩ and Cf = 100 nF.

Using:

`Vout = I × Rf`

the nominal outputs are:
- 1 µA → 47 mV
- 2 µA → 94 mV
- 3 µA → 141 mV

The nominal feedback pole is:

`fc = 1 / (2π Rf Cf) ≈ 33.9 Hz`

The capacitor is provisional. A real TIA compensation capacitor must be
selected using the actual probe capacitance, wiring capacitance, op-amp
open-loop behavior and desired noise bandwidth.

## Op-amp baseline

For a new implementation, LM358B is preferred over the older generic LM358.
TI lists LM358B as an active 3–36 V dual op-amp with improved offset and
bandwidth relative to the original LM358.

The TIA output is low-level, so the positive-rail output limitation is not the
main concern in this application; stability and input-current behavior are.

## ADC

ADS1115 is the high-resolution external ADC boundary:
- 16-bit
- 4-channel multiplexed input
- I2C
- PGA
- 2–5.5 V supply

For Branch B, choose the PGA range after the real TIA output is measured.
For Branch A, verify the selected PGA accommodates the complete 0–3 V output.

## Calibration

The SEN0237-A documentation calls for probe calibration because saturated
output varies between probes and with temperature. Two-point calibration can
be used for temperature variation.

PondGuard firmware should therefore store calibration coefficients rather
than assume one universal voltage-to-DO equation.

## Safety rule

Do not attach an unknown electrochemical probe to the custom TIA until:
- current polarity is measured
- maximum probe current is bounded
- the op-amp is stable with the probe/cable capacitance
- output range is confirmed
- ADC input limits are confirmed
