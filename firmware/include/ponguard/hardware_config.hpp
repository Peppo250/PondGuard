#pragma once

// Canonical M6.5 pin map.
// Source of truth: config/hardware.yaml
namespace ponguard::hw {

constexpr int PIN_NH3_ADC = 5;

// ADS1115 I2C
constexpr int PIN_I2C_SDA = 6;
constexpr int PIN_I2C_SCL = 7;

// DS18B20
constexpr int PIN_TEMPERATURE = 4;

// MicroSD GP-SPI
constexpr int PIN_SD_SCK  = 10;
constexpr int PIN_SD_MISO = 19;
constexpr int PIN_SD_MOSI = 18;
constexpr int PIN_SD_CS   = 3;

// SIM800L UART
constexpr int PIN_GSM_TX = 21;
constexpr int PIN_GSM_RX = 20;

// Logical actuator outputs -> external transistor/SSR driver stages
constexpr int PIN_AERATOR_RELAY = 0;
constexpr int PIN_DO_PUMP_RELAY = 1;

// No dedicated buzzer GPIO in M6.5.
constexpr int PIN_BUZZER = -1;

} // namespace ponguard::hw
