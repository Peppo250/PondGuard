# PondGuard M6.4 — NH3 Interface

## Critical sensor finding

The Fermion SEN0567 (DFRobot SKU SEN0567) is an analog MEMS NH3 sensor.
DFRobot specifies:
- detection range: 1–300 ppm
- supply: 3.3–5 V
- current: <20 mA
- analog-voltage output
- RL = 4.7 kΩ
- operating temperature: −10 to 50 °C
- operating humidity: 15–90%RH non-condensing

However, DFRobot explicitly labels the SEN0567 as **qualitative only** and
directs users needing quantitative measurements to a factory-calibrated
sensor.

This changes how PondGuard must treat the device.

## M6.4 architecture

```text
                 SENSOR SIDE
                    ┌─────────────┐
water / headspace → │ ePTFE wall  │
                    └──────┬──────┘
                           ↓
                     NH3-rich chamber
                           ↓
                    SEN0567 MEMS
                           ↓
                    Analog voltage
                           ↓
                 input protection /
                 RC anti-noise filter
                           ↓
                    ESP32-C3 ADC
```

The SEN0567 breakout has three connections:
- A = analog output
- VCC
- GND

## Supply decision

For a direct ESP32 ADC interface, the prototype should power the SEN0567 from
**3.3 V**, not 5 V, unless a verified resistor-divider/level-shifting stage
is added.

Reason: the ESP32-C3 ADC input must not be exposed to a sensor output that can
exceed the MCU supply domain.

With 3.3 V sensor supply, the nominal engineering assumption is that the
analog output remains within a 0–3.3 V envelope. This assumption still needs
verification on the actual breakout.

## Input protection

Recommended first-pass interface:

```text
SEN0567 A
   |
   +---- Rseries 1 kΩ ----+----> ESP32 ADC GPIO 5
                          |
                         C 100 nF
                          |
                         GND

Clamp/protection:
ADC node → Schottky clamp to 3.3 V and GND
```

The RC is for high-frequency electrical noise, not for making the sensor
quantitative.

A 1 kΩ / 100 nF pole is approximately 1.59 kHz, which is far above the
minutes-scale control loop and therefore should not distort the intended
slow NH3 trend signal.

## Chamber integration

The sensor is intended to sample gas, not dissolved ammonia directly.

The proposed PondGuard sampling chamber therefore needs:

```text
pond water
   ↓
gas-permeable hydrophobic membrane
   ↓
headspace
   ↓
SEN0567
```

A small fan can circulate headspace gas, but the chamber must be designed so
that:
- water cannot reach the sensor
- condensation is controlled
- the sensor's specified humidity range is respected
- external contaminants are minimized
- response time is characterized experimentally

## Important chemistry boundary

The SEN0567's ppm output is a **gas-phase observation**.

It is not valid to use a universal formula like:

`ppm → dissolved NH3 concentration in mg/L`

without experimentally characterizing:
- membrane permeability
- chamber volume
- gas/liquid partitioning
- temperature
- pH
- headspace mixing
- sensor response
- chamber leakage

Therefore the firmware should initially expose:

```text
nh3_gas_ppm_raw
```

and only later derive:

```text
estimated_free_nh3_mg_l
```

after a calibration model is established.

## Heater

The current DFRobot page specifies <20 mA operating current and 3.3–5 V
operation. No independent heater-control pin is exposed in the stated
three-pin breakout interface.

Therefore M6.4 does **not** assume a separately switched 750 mW heater or an exposed external heater-control pin.

The prior project architecture's proposed external heater switch should be
removed unless the exact purchased sensor variant/datasheet proves that an
external heater connection exists.

## Warm-up

DFRobot's usage guidance says the module needs more than 5 minutes of warm-up
on first use and recommends more than 24 hours after a long period of
non-use.

The firmware should therefore support a startup stabilization state:

```text
BOOT
  ↓
WARMUP
  ↓
BASELINE
  ↓
MEASUREMENT
```

and should not immediately treat the first raw readings as calibrated NH3.

## Contaminant protection

DFRobot warns against:
- volatile silicone compounds
- corrosive gases such as H2S/SOx/Cl2/HCl
- alkali/halogen contamination
- extreme temperature/humidity/pollution
- water/condensation/frost
- excessive vibration/impact

This is particularly important in a shrimp pond because H2S and high humidity
can be present.

## Calibration strategy

Because the SEN0567 is qualitative, calibration must be empirical.

Recommended sequence:

1. characterize clean-air baseline
2. expose to known NH3 gas concentrations in a controlled chamber
3. measure steady-state and transient voltage
4. fit an empirical response curve
5. characterize hysteresis and recovery
6. characterize temperature/humidity effects
7. only then construct a chamber-specific ppm estimate

If the research requires accurate quantitative NH3 measurement, use the
factory-calibrated electrochemical NH3 sensor as a benchmark/reference and
compare the low-cost MEMS route against it.

## M6.4 acceptance criteria

- exact electrical interface documented
- no >3.3 V assumption on ESP32 ADC
- input protection/filter specified
- sensor warm-up state defined
- qualitative-vs-quantitative limitation documented
- no unsupported ppm→mg/L conversion claimed
- chamber calibration plan defined
- BOM and preliminary schematic present
