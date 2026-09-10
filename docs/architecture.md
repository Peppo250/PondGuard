# PondGuard M1 Architecture

## Principle

M1 establishes stable interfaces before implementing control algorithms.

### Data path

```text
physical sensor
   ↓
electrical interface / signal conditioning
   ↓
sensor abstraction
   ↓
EnvironmentalSample
   ↓
future controller
```

### Control path

```text
future controller
   ↓
ActuatorCommand
   ↓
hardware driver
   ↓
relay / SSR
   ↓
physical actuator
```

The controller is intentionally not implemented in M1.

## Sensor abstractions

- `dissolved_oxygen_mg_l`
- `free_nh3_mg_l`
- `ph`
- `temperature_c`
- `battery_v`

Every reading carries:
- value
- validity flag
- timestamp

This keeps sensor errors explicit rather than encoding failure as a plausible numeric value.

## Actuator abstractions

- aerator
- DO circulation pump

The aerator has an explicit ON fail-safe requirement.

## Why configuration is separate

Hardware values are likely to change during prototyping. Keeping them in YAML allows tooling and agents to inspect one canonical configuration and later generate:
- firmware constants
- Wokwi diagrams
- test fixtures
- BOM tables
- documentation
