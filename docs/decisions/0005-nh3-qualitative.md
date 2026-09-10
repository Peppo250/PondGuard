# ADR 0005 — SEN0567 quantitative limitation

## Decision

Treat the SEN0567 as a qualitative NH3 gas sensor until a chamber-specific
empirical calibration is established.

## Reason

The vendor's current documentation explicitly says the MEMS sensor is for
qualitative measurement and directs quantitative users toward a factory-
calibrated gas sensor.

## Consequence

The firmware data model should preserve:
- raw sensor voltage
- baseline-normalized signal
- qualitative NH3 status

before any `mg/L free NH3` estimate is enabled.

A dissolved-NH3 estimate can be introduced later only with a measured transfer
function for the membrane/chamber/temperature/pH system.
