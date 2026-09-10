#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#include "ponguard_sim.h"

// ============================================================
// Pin map
// ============================================================

constexpr int AERATOR_PIN = 0;
constexpr int DO_PUMP_PIN = 1;

constexpr int SD_CS = 3;
constexpr int TEMP_PIN = 4;
constexpr int NH3_PIN = 2;

constexpr int I2C_SDA = 6;
constexpr int I2C_SCL = 7;

constexpr int SD_SCK = 10;
constexpr int SD_MISO = 19;
constexpr int SD_MOSI = 18;

constexpr int GSM_TX = 21;
constexpr int GSM_RX = 20;

// ============================================================
// Sensor / conversion constants
// ============================================================

constexpr float DO_FULL_SCALE_V = 3.0f;
constexpr float DO_FULL_SCALE_MG_L = 12.0f;

// Qualitative simulation scale only.
// This is NOT a validated dissolved-NH3 conversion.
constexpr float NH3_SIM_FULL_SCALE = 1.2f;

constexpr float PH_SLOPE_V_PER_PH = 0.05916f;

constexpr float BATTERY_DIVIDER_RATIO =
    (10000.0f + 3300.0f) / 3300.0f;

constexpr float BATTERY_ADC_MAX_V =
    8.4f / BATTERY_DIVIDER_RATIO;

// ============================================================
// ADS1115 register / I2C definitions
// ============================================================

constexpr uint8_t ADS1115_ADDR = 0x48;

constexpr uint8_t ADS_REG_CONVERSION = 0x00;
constexpr uint8_t ADS_REG_CONFIG = 0x01;

// ADS1115 configuration fields used by this simulation:
//
// OS     = 1              start single-shot conversion
// MUX    = 100..111       AIN0..AIN3 single-ended
// PGA    = 001            +/-4.096 V
// MODE   = 1              single-shot
// DR     = 100            128 SPS
// COMP   = 011            comparator disabled
//
constexpr uint16_t ADS_OS_START = 0x8000;
constexpr uint16_t ADS_PGA_4096 = 0x0200;
constexpr uint16_t ADS_MODE_SINGLE = 0x0100;
constexpr uint16_t ADS_DR_128SPS = 0x0080;
constexpr uint16_t ADS_COMP_DISABLE = 0x0003;

// ============================================================
// Hardware objects
// ============================================================

OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

SimController controller;

struct SimGsm {
  void print(const char *s) {
    (void)s;
  }
};

SimGsm gsm;

// ============================================================
// Runtime state
// ============================================================

bool sd_ready = false;
bool ads_ready = false;
bool sensor_fault_override = false;

uint32_t last_sample_ms = 0;
uint32_t last_gsm_ms = 0;
uint32_t pump_test_until_ms = 0;

// ============================================================
// Utility functions
// ============================================================

float clampf(float v, float lo, float hi) {
  if (v < lo) {
    return lo;
  }

  if (v > hi) {
    return hi;
  }

  return v;
}

// ============================================================
// ADS1115 low-level driver
// ============================================================

bool adsWriteRegister(uint8_t reg, uint16_t value) {
  Wire.beginTransmission(ADS1115_ADDR);

  if (Wire.write(reg) != 1) {
    Wire.endTransmission();
    return false;
  }

  if (Wire.write(static_cast<uint8_t>(value >> 8)) != 1) {
    Wire.endTransmission();
    return false;
  }

  if (Wire.write(static_cast<uint8_t>(value & 0xFF)) != 1) {
    Wire.endTransmission();
    return false;
  }

  return Wire.endTransmission() == 0;
}

bool adsReadRegister(uint8_t reg, uint16_t &value) {
  // Set register pointer.
  Wire.beginTransmission(ADS1115_ADDR);

  if (Wire.write(reg) != 1) {
    Wire.endTransmission();
    return false;
  }

  if (Wire.endTransmission(false) != 0) {
    return false;
  }

  // Read two-byte register.
  const uint8_t requested = 2;
  const uint8_t received =
      static_cast<uint8_t>(Wire.requestFrom(ADS1115_ADDR, requested));

  if (received != requested) {
    return false;
  }

  if (Wire.available() < 2) {
    return false;
  }

  const uint8_t msb = static_cast<uint8_t>(Wire.read());
  const uint8_t lsb = static_cast<uint8_t>(Wire.read());

  value = (static_cast<uint16_t>(msb) << 8) | lsb;

  return true;
}

bool adsProbe() {
  // The custom Wokwi ADS1115 responds at 0x48.
  Wire.beginTransmission(ADS1115_ADDR);

  if (Wire.endTransmission() != 0) {
    return false;
  }

  return true;
}

bool adsBegin() {
  if (!adsProbe()) {
    return false;
  }

  // Default configuration:
  // single-shot, AIN0, +/-4.096 V, 128 SPS, comparator disabled.
  constexpr uint16_t defaultConfig =
      ADS_OS_START |
      0x4000 |               // MUX AIN0
      ADS_PGA_4096 |
      ADS_MODE_SINGLE |
      ADS_DR_128SPS |
      ADS_COMP_DISABLE;

  if (!adsWriteRegister(ADS_REG_CONFIG, defaultConfig)) {
    return false;
  }

  return true;
}

bool adsStartSingleEnded(uint8_t channel) {
  if (channel > 3) {
    return false;
  }

  // MUX:
  // 100 = AIN0
  // 101 = AIN1
  // 110 = AIN2
  // 111 = AIN3
  const uint16_t mux =
      static_cast<uint16_t>(0x4000u |
                            (static_cast<uint16_t>(channel) << 12));

  const uint16_t config =
      ADS_OS_START |
      mux |
      ADS_PGA_4096 |
      ADS_MODE_SINGLE |
      ADS_DR_128SPS |
      ADS_COMP_DISABLE;

  return adsWriteRegister(ADS_REG_CONFIG, config);
}

int16_t adsReadSingleEnded(uint8_t channel) {
  if (!ads_ready) {
    return 0;
  }

  if (!adsStartSingleEnded(channel)) {
    return 0;
  }

  // Our custom Wokwi model completes the conversion immediately.
  uint16_t raw = 0;

  if (!adsReadRegister(ADS_REG_CONVERSION, raw)) {
    return 0;
  }

  return static_cast<int16_t>(raw);
}

float adsComputeVolts(int16_t counts) {
  // PGA = +/-4.096 V
  return static_cast<float>(counts) *
         (4.096f / 32768.0f);
}

float adcVolts(uint8_t channel) {
  return adsComputeVolts(adsReadSingleEnded(channel));
}

// ============================================================
// PondGuard conversions
// ============================================================

float doFromVoltage(float voltage) {
  const float clamped =
      clampf(voltage, 0.0f, DO_FULL_SCALE_V);

  return (clamped / DO_FULL_SCALE_V) *
         DO_FULL_SCALE_MG_L;
}

float pHFromDifferential(float signal_v, float bias_v) {
  return 7.0f +
         (bias_v - signal_v) / PH_SLOPE_V_PER_PH;
}

float batteryFromAdc(float adc_v) {
  const float clamped =
      clampf(adc_v, 0.0f, BATTERY_ADC_MAX_V);

  return clamped * BATTERY_DIVIDER_RATIO;
}

// ============================================================
// Test command handling
// ============================================================

void handleTestCommand(const String &line) {
  String cmd = line;

  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "TEST SENSOR_FAIL") {
    sensor_fault_override = true;

    // Immediate fail-safe output.
    digitalWrite(AERATOR_PIN, HIGH);

    Serial.println("TEST|SENSOR_FAIL=ARMED");
    Serial.println("TEST|FAILSAFE=AERATOR_ON");

  } else if (cmd == "TEST SENSOR_OK") {
    sensor_fault_override = false;

    Serial.println("TEST|SENSOR_OK=ARMED");

  } else if (cmd == "TEST GSM") {
    gsm.print("AT\r\n");

    last_gsm_ms = millis();

    Serial.println("TEST|GSM_TX=AT_SENT");

  } else if (cmd == "TEST PUMP") {
    pump_test_until_ms =
        millis() + 1500UL;

    digitalWrite(DO_PUMP_PIN, HIGH);

    Serial.println("TEST|PUMP=ON");

  } else if (cmd == "TEST STATUS") {
    Serial.printf(
        "STATUS|AER=%d|PUMP=%d|SD=%d|ADS=%d|SENSOR_FAULT=%d\n",
        digitalRead(AERATOR_PIN),
        digitalRead(DO_PUMP_PIN),
        sd_ready ? 1 : 0,
        ads_ready ? 1 : 0,
        sensor_fault_override ? 1 : 0);

  } else if (cmd.length() > 0) {
    Serial.printf(
        "TEST|UNKNOWN=%s\n",
        cmd.c_str());
  }
}

void processSerialCommands() {
  while (Serial.available()) {
    const String line =
        Serial.readStringUntil('\n');

    handleTestCommand(line);
  }
}

// ============================================================
// Result reporting
// ============================================================

void emitResult(
    const SimSample &sample,
    const SimOutput &output,
    bool valid,
    float do_v,
    float nh3_v,
    float ph_signal_v,
    float ph_bias_v,
    float battery_adc_v,
    float temp) {

  Serial.printf(
      "RESULT|ms=%lu|do=%.3f|nh3=%.3f|ph=%.3f|"
      "temp=%.3f|bat=%.3f|score=%.3f|aerator=%d|"
      "pump=%d|reason=%s|valid=%d\n",

      static_cast<unsigned long>(millis()),

      sample.do_mg_l,
      sample.nh3,
      sample.ph,
      sample.temp_c,
      sample.battery_v,

      output.score,

      output.aerator == SimActuatorState::ON ? 1 : 0,
      output.pump == SimActuatorState::ON ? 1 : 0,

      output.reason,

      valid ? 1 : 0);

  // Keep these parameters intentionally available for
  // debugging/future structured logging.
  (void)do_v;
  (void)nh3_v;
  (void)ph_signal_v;
  (void)ph_bias_v;
  (void)battery_adc_v;
  (void)temp;
}

// ============================================================
// Setup
// ============================================================

void setup() {
  Serial.begin(115200);

  delay(100);

  // ----------------------------------------------------------
  // Boot identification
  // ----------------------------------------------------------

  Serial.println(
      "BOOT|SIMULATION=M7.6_AUTOMATED_VALIDATION");

  Serial.println(
      "BOOT|FAILSAFE=AERATOR_ON");

  Serial.println(
      "BOOT|GSM_UART=READY");

  // ----------------------------------------------------------
  // GPIO safe-state configuration
  // ----------------------------------------------------------

  pinMode(AERATOR_PIN, OUTPUT);
  pinMode(DO_PUMP_PIN, OUTPUT);

  // Mandatory startup safety state:
  // aerator ON, measurement pump OFF.
  digitalWrite(AERATOR_PIN, HIGH);
  digitalWrite(DO_PUMP_PIN, LOW);

  // ----------------------------------------------------------
  // I2C / ADS1115
  // ----------------------------------------------------------

  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setTimeOut(50);

  ads_ready = adsBegin();

  Serial.printf(
      "BOOT|ADS1115=%s\n",
      ads_ready ? "PASS" : "FAIL");

  if (!ads_ready) {
    // Hard fail-safe.
    digitalWrite(AERATOR_PIN, HIGH);

    Serial.println(
        "BOOT|FAILSAFE=AERATOR_ON|"
        "REASON=ADS1115_INIT_FAIL");
  }

  // ----------------------------------------------------------
  // Temperature sensor
  // ----------------------------------------------------------

  tempSensor.begin();

  // ----------------------------------------------------------
  // SD card
  // ----------------------------------------------------------

  SPI.begin(
      SD_SCK,
      SD_MISO,
      SD_MOSI,
      SD_CS);

  sd_ready = SD.begin(SD_CS, SPI);

  Serial.printf(
      "BOOT|SD=%s\n",
      sd_ready ? "PASS" : "FAIL");

  // ----------------------------------------------------------
  // Command interface
  // ----------------------------------------------------------

  Serial.println(
      "READY|COMMANDS=TEST SENSOR_FAIL / "
      "TEST SENSOR_OK / TEST GSM / TEST PUMP / TEST STATUS");

  Serial.flush();

  // Start first sample interval from now.
  last_sample_ms = millis();
}

// ============================================================
// Main loop
// ============================================================

void loop() {
  processSerialCommands();

  const uint32_t now = millis();

  // ----------------------------------------------------------
  // Pump test override
  // ----------------------------------------------------------

  if (now < pump_test_until_ms) {
    digitalWrite(DO_PUMP_PIN, HIGH);
  }

  // ----------------------------------------------------------
  // If ADS1115 failed, remain in safe state.
  // ----------------------------------------------------------

  if (!ads_ready) {
    digitalWrite(AERATOR_PIN, HIGH);
    digitalWrite(DO_PUMP_PIN, LOW);

    delay(50);
    return;
  }

  // ----------------------------------------------------------
  // Sample every 2 seconds
  // ----------------------------------------------------------

  if (now - last_sample_ms < 2000UL) {
    delay(5);
    return;
  }

  last_sample_ms = now;

  // ----------------------------------------------------------
  // Acquire analog channels
  //
  // ADS A0 = pH signal
  // ADS A1 = DO
  // ADS A2 = battery
  // ADS A3 = pH bias
  // ----------------------------------------------------------

  const float do_v =
      adcVolts(1);

  const float ph_signal_v =
      adcVolts(0);

  const float ph_bias_v =
      adcVolts(3);

  const float battery_adc_v =
      adcVolts(2);

  // NH3 sensor is directly connected to ESP32 ADC GPIO5
  // in the Wokwi simulation.
  const float nh3_v =
      analogReadMilliVolts(NH3_PIN) / 1000.0f;

  // ----------------------------------------------------------
  // Temperature
  // ----------------------------------------------------------

  tempSensor.requestTemperatures();

  const float temp =
      tempSensor.getTempCByIndex(0);

  // ----------------------------------------------------------
  // Build normalized sample
  // ----------------------------------------------------------

  SimSample sample{};

  sample.do_mg_l =
      doFromVoltage(do_v);

  sample.nh3 =
      clampf(
          nh3_v / 3.3f,
          0.0f,
          1.0f) *
      NH3_SIM_FULL_SCALE;

  sample.ph =
      pHFromDifferential(
          ph_signal_v,
          ph_bias_v);

  sample.temp_c =
      temp;

  sample.battery_v =
      batteryFromAdc(
          battery_adc_v);

  sample.timestamp_ms =
      now;

  // ----------------------------------------------------------
  // Sensor validity
  // ----------------------------------------------------------

  const bool temperature_valid =
      isfinite(temp) &&
      temp != DEVICE_DISCONNECTED_C &&
      temp > -40.0f &&
      temp < 100.0f;

  const bool measured_valid =
      isfinite(sample.do_mg_l) &&
      isfinite(sample.nh3) &&
      isfinite(sample.ph) &&
      isfinite(sample.battery_v) &&
      temperature_valid;

  const bool valid =
      measured_valid &&
      !sensor_fault_override;

  // ----------------------------------------------------------
  // Simulation time
  // ----------------------------------------------------------

  const float hour =
      fmod(
          now / 10000.0f,
          24.0f);

  // ----------------------------------------------------------
  // PondGuard decision engine
  // ----------------------------------------------------------

  SimOutput output =
      controller.update(
          sample,
          hour,
          valid);

  // ----------------------------------------------------------
  // Pump test override ends
  // ----------------------------------------------------------

  if (now >= pump_test_until_ms) {
    output.pump =
        SimActuatorState::OFF;
  }

  // ----------------------------------------------------------
  // Hardware outputs
  // ----------------------------------------------------------

  if (!valid) {
    // Sensor failure / invalid telemetry:
    // aerator must remain ON.
    digitalWrite(
        AERATOR_PIN,
        HIGH);

    output.aerator =
        SimActuatorState::ON;
  } else {
    digitalWrite(
        AERATOR_PIN,
        output.aerator == SimActuatorState::ON
            ? HIGH
            : LOW);
  }

  if (now >= pump_test_until_ms) {
    digitalWrite(
        DO_PUMP_PIN,
        output.pump == SimActuatorState::ON
            ? HIGH
            : LOW);
  }

  // ----------------------------------------------------------
  // GSM heartbeat simulation
  // ----------------------------------------------------------

  if (now - last_gsm_ms >= 30000UL) {
    last_gsm_ms = now;

    gsm.print("AT\r\n");
  }

  // ----------------------------------------------------------
  // Human-readable telemetry
  // ----------------------------------------------------------

  Serial.printf(
      "TELEMETRY|DO=%.2f|NH3q=%.3f|pH=%.2f|"
      "T=%.2f|BAT=%.2f|score=%.1f|AER=%d|"
      "PUMP=%d|reason=%s\n",

      sample.do_mg_l,
      sample.nh3,
      sample.ph,
      sample.temp_c,
      sample.battery_v,

      output.score,

      output.aerator == SimActuatorState::ON
          ? 1
          : 0,

      output.pump == SimActuatorState::ON
          ? 1
          : 0,

      output.reason);

  // ----------------------------------------------------------
  // Machine-readable validation result
  // ----------------------------------------------------------

  emitResult(
      sample,
      output,
      valid,
      do_v,
      nh3_v,
      ph_signal_v,
      ph_bias_v,
      battery_adc_v,
      temp);
}