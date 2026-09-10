# PondGuard M5 — Wokwi Harness

## Purpose

M5 validates that the M4 ESP32-C3 firmware can be wired to a simulated
microcontroller/peripheral environment.

## Simulation boundary

Wokwi models:
- ESP32-C3
- analog sensor interfaces using potentiometers
- DS18B20 temperature
- microSD
- relay outputs
- status LEDs
- buzzer

The analog potentiometers represent **conditioned sensor signals**, not the
physical chemistry of:
- galvanic DO
- pH glass electrode
- SEN0567 / NH3 diffusion chamber
- battery charging

Those physical/electrical subsystems are intentionally left for M6.

## Running in Wokwi

The generated files are:
- `generated/diagram.json`
- `generated/sketch.ino`

They can be copied into a Wokwi ESP32-C3 project.

## Demonstration

1. Start simulation.
2. Observe normal values in Serial Monitor.
3. Lower the DO potentiometer.
4. Observe the crash score change.
5. At low DO, observe relay/LED 1 activate.
6. Increase DO above the release region and observe hysteresis.
7. Adjust the NH3 potentiometer and temperature to explore combined risk.
8. Watch `pondguard.csv` in the simulated SD card.

Never connect a simulated relay output to actual mains equipment.
