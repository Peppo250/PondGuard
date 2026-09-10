# PondGuard M6.3 — pH Analog Front-End

## Engineering finding

A raw pH electrode produces a **bipolar** voltage and has high source
resistance. On a single-supply embedded system, the signal therefore needs
both:
1. a very-high-input-impedance buffer, and
2. a level-shift/reference strategy so the electrode signal remains inside
   the ADC's valid common-mode/input range.

Analog Devices' CN0326 uses AD8603 as a high-impedance buffer for a pH
electrode and explicitly emphasizes guarding, shielding and high insulation
resistance at the electrode input.

Texas Instruments' pH-electrode application note shows the single-supply
level-shift approach: bias the reference electrode at a mid/offset voltage
and buffer the measuring electrode separately.

## M6.3 decision

The original M6.2 concept called for one AD8603. For the complete single-supply
pH interface, **one amplifier is not sufficient for the recommended buffered
level-shift topology**.

Therefore the preferred implementation is:

```text
                3.3 V
                  |
               10 kΩ
                  |
                  +----> AD8607 A (voltage follower)
                  |           |
               10 kΩ          +----> VPH_BIAS ≈ 1.65 V
                  |                         |
                 GND                        |
                                           |
                                pH reference electrode
                                           |
                                  Glass measurement cell
                                           |
                                   pH measurement electrode
                                           |
                                      AD8607 B
                                           |
                                   VPH_SIGNAL
                                           |
                                      ADS1115 AIN0+
                                           |
                                ADS1115 AIN3- = VPH_BIAS
                                           |
                                           I²C
                                           ↓
                                       ESP32-C3
```

### Why AD8607?

AD8607 is the dual-channel member of the AD8603/AD8607/AD8609 family.
This gives two precision micropower rail-to-rail channels in one package:
- channel A: low-impedance 1.65 V bias buffer
- channel B: high-impedance pH electrode buffer

This preserves the project's preferred AD860x device family while avoiding
the need for two separate packages.

An alternative is two AD8603 packages. That is electrically valid but less
compact.

## ADC connection

The preferred measurement is differential:

```text
AIN0 = VPH_SIGNAL
AIN3 = VPH_BIAS
```

The ADC then measures approximately:

`VPH_DIFF = VPH_SIGNAL - VPH_BIAS`

The large DC bias is therefore removed digitally while keeping both physical
ADC inputs inside the 0–3.3 V supply range.

ADS1115 supports differential inputs, 16-bit conversion, programmable gain,
and I²C.

A ±0.512 V PGA range is a strong initial candidate because typical pH
electrode sensitivity is about 59.16 mV/pH at 25 °C and the full pH 0–14
span is approximately ±0.414 V around pH 7.

The actual pH probe voltage range and temperature span must be measured before
freezing the PGA range.

## pH-to-voltage relationship

At 25 °C the ideal Nernst slope is approximately 59.16 mV/pH.

A convenient centered model is:

`VPH_DIFF ≈ S(T) × (7 - pH)`

where:
- `S(T) = 2.303RT/F`
- T is absolute temperature
- R is the gas constant
- F is Faraday's constant

The sign convention must be confirmed experimentally with the purchased
probe because connector orientation and probe polarity determine whether the
voltage rises or falls with pH.

## Bias generation

The 1.65 V bias starts as:

`3.3 V / 2 = 1.65 V`

using two 10 kΩ resistors.

The midpoint must be buffered before it is connected to the pH reference
electrode. Do not connect the raw divider directly to the high-impedance
measurement node as a substitute for a buffer.

The 10 kΩ / 10 kΩ divider consumes approximately 165 µA from the 3.3 V rail,
before accounting for buffer current.

For very low-power production design, a lower-loss reference/bias source can
be evaluated later, but the buffered divider is transparent and appropriate
for the first prototype.

## Output filtering

Analog Devices CN0326 uses a 10 kΩ / 1 µF output low-pass arrangement,
approximately 16 Hz, for the buffered pH channel.

PondGuard may use a smaller RC if the final sampling/control loop needs more
bandwidth, but the first prototype should include a documented RC filter
after the measurement buffer.

## PCB layout requirements

The pH electrode node is high impedance and should be physically protected:
- keep the electrode trace short
- maintain large clearance from switching nodes
- avoid running it beside GSM or relay traces
- use a driven guard strategy where appropriate
- use clean high-insulation PCB material/geometry
- shield the connector/cable against RF noise
- keep flux/residue away from the high-impedance node

Do not treat a generic breadboard as a representative final pH PCB layout.

## Calibration

Use a minimum of two reference buffer solutions:
- pH 7 is the preferred zero/offset point
- pH 4 or pH 10 can provide a second span point depending on deployment

Store calibration coefficients in firmware.

Temperature compensation should use the DS18B20 reading and the temperature
dependence of the pH electrode's Nernst slope.

## M6.3 acceptance criteria

1. dual-buffer topology defined
2. electrode bias defined
3. ADS1115 differential channels defined
4. Nernst conversion model defined
5. calibration strategy defined
6. layout/protection rules documented
7. calculations and preliminary circuit artifact present
8. no claim of measured pH accuracy
