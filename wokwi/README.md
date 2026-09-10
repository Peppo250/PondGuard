# PondGuard M7.1 — Complete Wokwi Hardware-Interface Simulation

M7.1 upgrades the legacy M5 Wokwi harness to the M6.7 collision-free hardware map.

## Scope

This simulation validates the connection-level behavior of:

- ESP32-C3
- ADS1115 (custom Wokwi chip model, I2C address 0x48)
- DO interface voltage -> ADS1115 AIN1
- pH signal/bias -> ADS1115 AIN0/AIN3
- battery divider-equivalent voltage -> ADS1115 AIN2
- SEN0567-equivalent analog output -> GPIO5
- DS18B20 -> GPIO4
- MicroSD -> SPI GPIO10/18/19, CS GPIO3
- GSM UART interface -> GPIO20/21
- aerator logical driver -> GPIO0
- DO circulation pump logical driver -> GPIO1
- logic analyzer observation of I2C/SPI/UART signals

## Important simulation boundary

Wokwi provides useful digital and basic analog simulation, but it does not replace the M6.7 SPICE/calculation domain for detailed regulator/analog accuracy. The potentiometers therefore represent the **electrical output nodes** of the corresponding conditioned sensor interfaces. The custom ADS1115 model then converts those voltages to digital readings over I2C.

The SEN0567 path remains qualitative; its pot only exercises the firmware's qualitative gas input path.

## Run

Open `generated/diagram.json` in Wokwi and use `generated/sketch.ino` with `generated/libraries.txt`.

The logic analyzer captures:

`I2C_SCL, I2C_SDA, SD_MOSI, SD_MISO, SD_SCK, SD_CS, GSM_TX, GSM_RX`.
