# PondGuard M7.6 — Full Automated Hardware Simulation Validation

## FINAL STATUS: **FAIL**

This is a strict reproducibility pipeline. Missing PlatformIO/Wokwi CLI is a failure, not a skip.

## Stage Results

| Stage | Status | Exit | Time (s) |
|---|---:|---:|---:|
| python-regression | **PASS** | 0 | 6.12 |
| native-build | **PASS** | 0 | 4.88 |
| native-smoke | **PASS** | 0 | 0.80 |
| wokwi-firmware-build | **PASS** | 0 | 6.53 |
| wokwi-artifact-check | **PASS** | 0 | 0.00 |
| wokwi-lint | **PASS** | 0 | 6.78 |
| wokwi:01_nominal.yaml:run1 | **FAIL** | 1 | 3.65 |
| wokwi:01_nominal.yaml:run2 | **FAIL** | 1 | 2.94 |
| wokwi:04_battery_low.yaml:run1 | **FAIL** | 1 | 5.13 |
| wokwi:04_battery_low.yaml:run2 | **FAIL** | 124 | 90.04 |

## Wokwi Scenario Evidence

| Scenario | Run | Process | Acceptance | RESULT records | Hash | Repeat |
|---|---:|---:|---:|---:|---|---|
| 01_nominal.yaml | 1 | FAIL | FAIL | 0 | `4f53cda18c2baa0c…` | — |
| 01_nominal.yaml | 2 | FAIL | FAIL | 0 | `4f53cda18c2baa0c…` | PASS |
| 04_battery_low.yaml | 1 | FAIL | FAIL | 0 | `4f53cda18c2baa0c…` | — |
| 04_battery_low.yaml | 2 | FAIL | FAIL | 0 | `4f53cda18c2baa0c…` | PASS |

## What constitutes 100% pass

Every declared acceptance gate must pass: toolchain presence, Python/native regression, real ESP32-C3 firmware build, Wokwi diagram lint, every Wokwi scenario assertion, serial RESULT emission, repeatability, and artifact generation.

## Important limitation

This proves the declared **simulation contract** reproducibly. It does not prove physical hardware behavior, pond chemistry, sensor calibration, component tolerances beyond the modeled domains, or field reliability. Those require physical test evidence.
