# PondGuard Agent Instructions

## Mission

Develop PondGuard as a code-first embedded aquaculture control system.

## Source of truth

Treat these as authoritative repository inputs:

- `config/hardware.yaml` — hardware interfaces and pin map
- `config/thresholds.yaml` — control parameters and status
- `config/simulation.yaml` — simulation behavior
- `docs/` — engineering decisions and rationale

Do not silently duplicate hardware pin assignments in source files.

## Safety

1. The aerator is the fail-safe environmental actuator.
2. A sensor/control fault must never silently result in an unsafe "normal" state.
3. Do not implement continuous biological-agent dosing.
4. Do not connect simulated relay outputs directly to mains in a software demo.
5. Treat all relay states as logical control outputs unless a real hardware interface is explicitly documented.

## Scientific integrity

1. Clearly distinguish proposed thresholds from measured values.
2. Clearly distinguish simulation results from bench/field measurements.
3. Never claim sensor accuracy without experimental validation.
4. Do not claim that a machine-learning model is superior without comparative data.
5. Never fabricate sensor specifications.

## Change workflow

For hardware-related changes:

1. edit `config/hardware.yaml`
2. validate configuration
3. update sensor/actuator abstractions
4. update tests
5. update downstream simulation/Wokwi artifacts later

For control-related changes:

1. edit `config/thresholds.yaml`
2. add/update tests
3. document the engineering decision
4. only then update firmware behavior

## Coding style

- Prefer small modules with explicit interfaces.
- Avoid hidden global state.
- Use SI units in internal data structures.
- Store gas concentration explicitly as `mg/L` where the project model represents dissolved free NH3.
- Use `float` for first implementation; optimize only after profiling.
- Fail loudly in development builds.

## Current milestone: M7.1


## M4 rules

- Keep controller logic platform-independent.
- Arduino APIs belong only in `firmware/src/platform/` or hardware drivers.
- Native tests must not require ESP32 hardware.
- Treat sensor conversion constants as provisional until bench calibration.
- Preserve aerator fail-safe ON behavior.


## M6.5 rules

- `config/hardware.yaml` is the source of truth for pin allocation.
- ADS1115 owns DO, pH and battery high-resolution analog acquisition.
- SEN0567 remains on GPIO5 with the M6.4 input protection network.
- GPIO2/GPIO8/GPIO9 are avoided because they are strapping pins.
- GPIO18/GPIO19 are intentionally consumed by MicroSD SPI; USB-JTAG is therefore disabled when configured that way.
- GSM uses a dedicated ~4.0 V rail; never power SIM800L from 5 V or the low-current 3.3 V rail.
- Relay outputs are logical signals to external driver/SSR stages; never connect MCU GPIO directly to mains loads.
- Aerator safe state is ON; DO circulation pump safe state is OFF.
- Native tests must remain independent of ESP32 hardware.
