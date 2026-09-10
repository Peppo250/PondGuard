#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_ADS1X15.h>
#include "ponguard_sim.h"

namespace {
constexpr int AERATOR_PIN = 0;
constexpr int DO_PUMP_PIN = 1;
constexpr int SD_CS = 3;
constexpr int TEMP_PIN = 4;
constexpr int NH3_PIN = 5;
constexpr int I2C_SDA = 6;
constexpr int I2C_SCL = 7;
constexpr int SD_SCK = 10;
constexpr int SD_MISO = 19;
constexpr int SD_MOSI = 18;
constexpr int GSM_TX = 21;
constexpr int GSM_RX = 20;

constexpr float DO_FULL_SCALE_V = 3.0f;
constexpr float DO_FULL_SCALE_MG_L = 12.0f;
constexpr float NH3_SIM_FULL_SCALE = 1.2f; // Qualitative test scale only.
constexpr float PH_SLOPE_V_PER_PH = 0.05916f;
constexpr float BATTERY_DIVIDER_RATIO = (10000.0f + 3300.0f) / 3300.0f;
constexpr float BATTERY_ADC_MAX_V = 8.4f / BATTERY_DIVIDER_RATIO;

OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);
Adafruit_ADS1115 ads;
HardwareSerial gsm(1);
SimController controller;
bool sd_ready = false;
uint32_t last_sample_ms = 0;
uint32_t last_gsm_ms = 0;

float clampf(float v, float lo, float hi) {
  return v < lo ? lo : (v > hi ? hi : v);
}

float adcVolts(uint8_t ch) {
  return ads.computeVolts(ads.readADC_SingleEnded(ch));
}

float doFromVoltage(float v) {
  return clampf(v, 0.0f, DO_FULL_SCALE_V) / DO_FULL_SCALE_V * DO_FULL_SCALE_MG_L;
}

float pHFromDifferential(float signal_v, float bias_v) {
  return 7.0f + (bias_v - signal_v) / PH_SLOPE_V_PER_PH;
}

float batteryFromAdc(float adc_v) {
  return clampf(adc_v, 0.0f, BATTERY_ADC_MAX_V) * BATTERY_DIVIDER_RATIO;
}

void printRailModel() {
  Serial.println("Power model: 2S battery -> 5V / 3V3 / ~4V GSM rails");
  Serial.println("Wokwi scope: connection/digital-interface simulation; regulator analog behavior remains M6.7 SPICE/calculation domain.");
}

void logToSD(const SimSample &s, const SimOutput &o) {
  if (!sd_ready) return;
  File f = SD.open("/pondguard.csv", FILE_APPEND);
  if (!f) return;
  if (f.size() == 0) f.println("ms,do_mg_l,nh3_qual,pH,temp_c,battery_v,score,trend,aerator,pump,reason");
  f.printf("%lu,%.3f,%.3f,%.3f,%.2f,%.2f,%.2f,%.4f,%d,%d,%s\n",
           millis(), s.do_mg_l, s.nh3, s.ph, s.temp_c, s.battery_v, o.score, o.trend,
           o.aerator == SimActuatorState::ON, o.pump == SimActuatorState::ON, o.reason);
  f.close();
}

void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(AERATOR_PIN, OUTPUT);
  pinMode(DO_PUMP_PIN, OUTPUT);
  // Safety invariant: aerator ON until the control path establishes a valid state.
  digitalWrite(AERATOR_PIN, HIGH);
  digitalWrite(DO_PUMP_PIN, LOW);

  Wire.begin(I2C_SDA, I2C_SCL);
  if (!ads.begin(0x48, &Wire)) {
    Serial.println("ERROR: ADS1115 not detected on 0x48");
    // Keep aerator ON if the acquisition bus is unavailable.
    digitalWrite(AERATOR_PIN, HIGH);
  } else {
    ads.setGain(GAIN_ONE); // ±4.096 V; protects the 0–3.3 V analog domain.
    Serial.println("ADS1115: 0x48, PGA=GAIN_ONE (±4.096 V)");
  }

  tempSensor.begin();
  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  sd_ready = SD.begin(SD_CS);
  Serial.println(sd_ready ? "MicroSD: READY" : "MicroSD: unavailable (non-fatal in simulation)");

  // GSM UART interface only. No real cellular modem is present in Wokwi;
  // TX/RX are exposed to the logic analyzer for electrical-interface validation.
  gsm.begin(9600, SERIAL_8N1, GSM_RX, GSM_TX);

  Serial.println();
  Serial.println("============================================");
  Serial.println(" PondGuard M7.1 - Complete Wokwi Interface");
  Serial.println("============================================");
  Serial.println("DO   -> ADS1115 AIN1");
  Serial.println("pH   -> ADS1115 AIN0 with AIN3 bias");
  Serial.println("BAT  -> ADS1115 AIN2 after divider model");
  Serial.println("NH3  -> ESP32 GPIO5 protected ADC input");
  Serial.println("TEMP -> DS18B20 GPIO4");
  Serial.println("SD   -> SPI GPIO10/18/19, CS=3");
  Serial.println("GSM  -> UART GPIO20/21 (interface only)");
  Serial.println("AER  -> GPIO0 (safe state ON)");
  Serial.println("PUMP -> GPIO1 (safe state OFF)");
  printRailModel();
}

void loop() {
  const uint32_t now = millis();
  if (now - last_sample_ms < 5000UL) return;
  last_sample_ms = now;

  const float do_v = adcVolts(1);
  const float ph_signal_v = adcVolts(0);
  const float ph_bias_v = adcVolts(3);
  const float battery_adc_v = adcVolts(2);
  const float nh3_v = analogReadMilliVolts(NH3_PIN) / 1000.0f;

  tempSensor.requestTemperatures();
  const float temp = tempSensor.getTempCByIndex(0);

  SimSample sample{};
  sample.do_mg_l = doFromVoltage(do_v);
  sample.nh3 = clampf(nh3_v / 3.3f, 0.0f, 1.0f) * NH3_SIM_FULL_SCALE;
  sample.ph = pHFromDifferential(ph_signal_v, ph_bias_v);
  sample.temp_c = temp;
  sample.battery_v = batteryFromAdc(battery_adc_v);
  sample.timestamp_ms = now;
  sample.valid = isfinite(sample.do_mg_l) && isfinite(sample.nh3) && isfinite(sample.ph) &&
                 isfinite(sample.temp_c) && isfinite(sample.battery_v) && temp > -40 && temp < 100;

  const float hour = fmod((now / 10000.0f), 24.0f); // accelerated visual day/night cycle
  SimOutput output = controller.update(sample, hour);
  output.pump = (((now / 1000UL) % 35UL) < 5UL) ? SimActuatorState::ON : SimActuatorState::OFF;

  digitalWrite(AERATOR_PIN, output.aerator == SimActuatorState::ON ? HIGH : LOW);
  digitalWrite(DO_PUMP_PIN, output.pump == SimActuatorState::ON ? HIGH : LOW);

  if (now - last_gsm_ms >= 30000UL) {
    last_gsm_ms = now;
    gsm.print("AT\r\n");
  }

  logToSD(sample, output);

  Serial.printf(
    "t=%lus | Vdo=%.3f DO=%.2f | Vnh3=%.3f NH3q=%.3f | Vph=%.3f Vbias=%.3f pH=%.2f | BATadc=%.3f BAT=%.2f | T=%.2f | score=%.1f | AER=%s PUMP=%s | %s\n",
    now / 1000UL, do_v, sample.do_mg_l, nh3_v, sample.nh3,
    ph_signal_v, ph_bias_v, sample.ph, battery_adc_v, sample.battery_v, sample.temp_c,
    output.score,
    output.aerator == SimActuatorState::ON ? "ON" : "OFF",
    output.pump == SimActuatorState::ON ? "ON" : "OFF",
    output.reason);
}
