#ifdef ARDUINO

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_ADS1X15.h>
#include <esp_task_wdt.h>

#include "ponguard/arduino_hardware.hpp"
#include "ponguard/hardware_config.hpp"
#include "ponguard/config.hpp"

namespace {
OneWire* g_one_wire = nullptr;
DallasTemperature* g_temp = nullptr;
Adafruit_ADS1115 g_ads;

float adsVolts(int16_t raw) {
    return g_ads.computeVolts(raw);
}

float batteryFromDivider(float v_adc) {
    return v_adc * ((10000.0f + 3300.0f) / 3300.0f);
}

} // namespace

namespace ponguard {

ArduinoHardwareSensors::ArduinoHardwareSensors() {}

void ArduinoHardwareSensors::begin() {
    analogReadResolution(12);

    // NH3 is the only direct MCU ADC channel in M6.5.
    pinMode(config::NH3_ANALOG_PIN, INPUT);

    Wire.begin(hw::PIN_I2C_SDA, hw::PIN_I2C_SCL);
    g_ads.begin(0x48);
    g_ads.setGain(GAIN_ONE); // ±4.096 V; conservative common domain

    g_one_wire = new OneWire(hw::PIN_TEMPERATURE);
    g_temp = new DallasTemperature(g_one_wire);
    g_temp->begin();

    SPI.begin(hw::PIN_SD_SCK, hw::PIN_SD_MISO, hw::PIN_SD_MOSI, hw::PIN_SD_CS);
    // SD initialization is best-effort; logging is handled by a later M6.x layer.
    SD.begin(hw::PIN_SD_CS);
}

EnvironmentalSample ArduinoHardwareSensors::read() {
    const uint32_t now = millis();

    // M6.5 ADS1115 channels:
    // AIN0 = pH signal, AIN1 = DO, AIN2 = battery divider, AIN3 = pH bias.
    const int16_t ph_signal_raw = g_ads.readADC_SingleEnded(0);
    const int16_t do_raw = g_ads.readADC_SingleEnded(1);
    const int16_t battery_raw = g_ads.readADC_SingleEnded(2);
    const int16_t ph_bias_raw = g_ads.readADC_SingleEnded(3);

    const float nh3_v = analogReadMilliVolts(config::NH3_ANALOG_PIN) / 1000.0f;
    const float do_v = adsVolts(do_raw);
    const float ph_signal_v = adsVolts(ph_signal_raw);
    const float ph_bias_v = adsVolts(ph_bias_raw);
    const float battery_v_adc = adsVolts(battery_raw);

    g_temp->requestTemperatures();
    const float temp = g_temp->getTempCByIndex(0);

    // These conversions remain provisional until bench calibration.
    const float do_mg_l = (do_v / 3.0f) * 12.0f;
    const float nh3_qualitative = (nh3_v / 3.3f) * 1.2f;
    const float ph = 7.0f + ((ph_bias_v - ph_signal_v) / 0.05916f);
    const float battery_v = batteryFromDivider(battery_v_adc);

    EnvironmentalSample sample{};
    sample.dissolved_oxygen_mg_l = {do_mg_l, isfinite(do_mg_l), now};
    sample.free_nh3_mg_l = {nh3_qualitative, isfinite(nh3_qualitative), now};
    sample.ph = {ph, isfinite(ph), now};
    sample.temperature_c = {temp, temp > -100.0f && temp < 100.0f, now};
    sample.battery_v = {battery_v, isfinite(battery_v), now};

    last_ = sample;
    return sample;
}

ArduinoActuators::ArduinoActuators() {}

void ArduinoActuators::begin() {
    pinMode(hw::PIN_AERATOR_RELAY, OUTPUT);
    pinMode(hw::PIN_DO_PUMP_RELAY, OUTPUT);

    // Safe startup state: aerator ON, DO circulation pump OFF.
    digitalWrite(hw::PIN_AERATOR_RELAY, HIGH);
    digitalWrite(hw::PIN_DO_PUMP_RELAY, LOW);

    // M6.5 watchdog: hardware WDT is reset only by a healthy application loop.
    esp_task_wdt_init(8, true);
    esp_task_wdt_add(NULL);
}

void ArduinoActuators::apply(const ActuatorCommand& command) {
    digitalWrite(
        hw::PIN_AERATOR_RELAY,
        command.aerator == ActuatorState::ON ? HIGH : LOW
    );
    digitalWrite(
        hw::PIN_DO_PUMP_RELAY,
        command.do_circulation_pump == ActuatorState::ON ? HIGH : LOW
    );
    esp_task_wdt_reset();
}

} // namespace ponguard

#endif
