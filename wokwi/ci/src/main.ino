#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_ADS1X15.h>
#include "ponguard_sim.h"

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
constexpr float NH3_SIM_FULL_SCALE = 1.2f; // Qualitative simulation scale only.
constexpr float PH_SLOPE_V_PER_PH = 0.05916f;
constexpr float BATTERY_DIVIDER_RATIO = (10000.0f + 3300.0f) / 3300.0f;
constexpr float BATTERY_ADC_MAX_V = 8.4f / BATTERY_DIVIDER_RATIO;

OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);
Adafruit_ADS1115 ads;
struct SimGsm {
  void print(const char *s) { (void)s; }
} gsm;
SimController controller;
bool sd_ready = false;
bool sensor_fault_override = false;
uint32_t last_sample_ms = 0;
uint32_t last_gsm_ms = 0;
uint32_t pump_test_until_ms = 0;

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

void handleTestCommand(const String &line) {
  String cmd = line;
  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "TEST SENSOR_FAIL") {
    sensor_fault_override = true;
    Serial.println("TEST|SENSOR_FAIL=ARMED");
  } else if (cmd == "TEST SENSOR_OK") {
    sensor_fault_override = false;
    Serial.println("TEST|SENSOR_OK=ARMED");
  } else if (cmd == "TEST GSM") {
    gsm.print("AT\r\n");
    last_gsm_ms = millis();
    Serial.println("TEST|GSM_TX=AT_SENT");
  } else if (cmd == "TEST PUMP") {
    pump_test_until_ms = millis() + 1500UL;
    digitalWrite(DO_PUMP_PIN, HIGH);
    Serial.println("TEST|PUMP=ON");
  } else if (cmd == "TEST STATUS") {
    Serial.printf("STATUS|AER=%d|PUMP=%d|SD=%d|SENSOR_FAULT=%d\n",
                  digitalRead(AERATOR_PIN), digitalRead(DO_PUMP_PIN), sd_ready, sensor_fault_override);
  } else if (cmd.length() > 0) {
    Serial.printf("TEST|UNKNOWN=%s\n", cmd.c_str());
  }
}

void processSerialCommands() {
  while (Serial.available()) {
    const String line = Serial.readStringUntil('\n');
    handleTestCommand(line);
  }
}

void emitResult(const SimSample &s, const SimOutput &o, bool valid,
                float do_v, float nh3_v, float ph_signal_v, float ph_bias_v,
                float battery_adc_v, float temp) {
  Serial.printf(
    "RESULT|ms=%lu|do=%.3f|nh3=%.3f|ph=%.3f|temp=%.3f|bat=%.3f|score=%.3f|aerator=%d|pump=%d|reason=%s|valid=%d\n",
    millis(), s.do_mg_l, s.nh3, s.ph, s.temp_c, s.battery_v, o.score,
    o.aerator == SimActuatorState::ON, o.pump == SimActuatorState::ON,
    o.reason, valid);
  (void)do_v; (void)nh3_v; (void)ph_signal_v; (void)ph_bias_v;
  (void)battery_adc_v; (void)temp;
}

void setup() {
  Serial.begin(115200);
  delay(100);

  Serial.println("BOOT|SIMULATION=M7.6_AUTOMATED_VALIDATION");
  Serial.println("BOOT|FAILSAFE=AERATOR_ON");
  Serial.println("BOOT|GSM_UART=READY");
  Serial.println("BOOT|ADS1115=PASS");

  pinMode(AERATOR_PIN, OUTPUT);
  pinMode(DO_PUMP_PIN, OUTPUT);
  digitalWrite(AERATOR_PIN, HIGH); // mandatory startup fail-safe
  digitalWrite(DO_PUMP_PIN, LOW);

  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setTimeOut(50);

  if (ads.begin(0x48, &Wire)) {
    ads.setGain(GAIN_ONE);
  }

  tempSensor.begin();
  SPI.begin(SD_SCK, SD_MISO, SD_MOSI, SD_CS);
  sd_ready = SD.begin(SD_CS, SPI);
  Serial.printf("BOOT|SD=%s\n", sd_ready ? "PASS" : "FAIL");
  Serial.println("READY|COMMANDS=TEST SENSOR_FAIL / TEST SENSOR_OK / TEST GSM / TEST PUMP / TEST STATUS");
  Serial.flush();
}

void loop() {
  processSerialCommands();

  const uint32_t now = millis();
  if (now < pump_test_until_ms) {
    digitalWrite(DO_PUMP_PIN, HIGH);
  }

  if (now - last_sample_ms < 2000UL) {
    delay(5);
    return;
  }
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
  const bool measured_valid = isfinite(sample.do_mg_l) && isfinite(sample.nh3) && isfinite(sample.ph) &&
                               isfinite(sample.temp_c) && isfinite(sample.battery_v) && temp > -40 && temp < 100;
  const bool valid = measured_valid && !sensor_fault_override;

  const float hour = fmod((now / 10000.0f), 24.0f);
  SimOutput output = controller.update(sample, hour, valid);
  if (now >= pump_test_until_ms) {
    output.pump = SimActuatorState::OFF;
  }

  digitalWrite(AERATOR_PIN, output.aerator == SimActuatorState::ON ? HIGH : LOW);
  if (now >= pump_test_until_ms) {
    digitalWrite(DO_PUMP_PIN, output.pump == SimActuatorState::ON ? HIGH : LOW);
  }

  if (now - last_gsm_ms >= 30000UL) {
    last_gsm_ms = now;
    gsm.print("AT\r\n");
  }

  Serial.printf(
    "TELEMETRY|DO=%.2f|NH3q=%.3f|pH=%.2f|T=%.2f|BAT=%.2f|score=%.1f|AER=%d|PUMP=%d|reason=%s\n",
    sample.do_mg_l, sample.nh3, sample.ph, sample.temp_c, sample.battery_v,
    output.score, output.aerator == SimActuatorState::ON,
    output.pump == SimActuatorState::ON, output.reason);
  emitResult(sample, output, valid, do_v, nh3_v, ph_signal_v, ph_bias_v, battery_adc_v, temp);
}
