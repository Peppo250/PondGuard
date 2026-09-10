# M6.6 External Verification Sources

- Espressif ESP32-C3 hardware schematic checklist: strapping pins GPIO2, GPIO8, GPIO9.
- Espressif ESP32-C3 API reference: GPIO18/GPIO19 are USB-JTAG by default; GPIO12–17 are normally used for SPI flash/PSRAM.
- Texas Instruments ADS1115 Rev. E datasheet: 16-bit, 4-channel multiplexed ADC; 2.0–5.5 V supply; analog inputs constrained to GND..VDD.

Web sources checked on 2026-09-07:
- https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html
- https://docs.espressif.com/projects/esp-idf/en/release-v5.1/esp32c3/esp-idf-en-v5.1.7-1-g4b1ae715b8-esp32c3.pdf
- https://www.ti.com/lit/ds/symlink/ads1115.pdf
