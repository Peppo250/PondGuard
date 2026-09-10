# ADR 0006 — Unified ESP32-C3 Peripheral Allocation

## Decision

Adopt the M6.5 pin map in `config/hardware.yaml` and
`config/pinmap_m6_5.json`.

## Rationale

The previous map had two concrete conflicts:
1. GPIO6/GPIO7 were simultaneously treated as analog inputs and I2C pins.
2. GPIO20 was assigned to both GSM RX and the buzzer.

M6.5 resolves this by moving DO, pH and battery acquisition onto ADS1115,
keeping NH3 on GPIO5, removing the dedicated buzzer GPIO, and allocating
a non-conflicting SPI/UART/1-Wire/GPIO map.

## Trade-off

GPIO18/19 are used for the MicroSD SPI bus. Espressif documents these pins
as USB-JTAG pins; using them as regular GPIO disables USB-JTAG. Development
can continue through an external UART interface or a development board's
alternate serial path.

## Safety

Actuator GPIOs are only logical outputs into external driver stages.
The aerator remains the environmental fail-safe actuator and must default ON.
