#pragma once

namespace ponguard::config {

struct ControlThresholds {
    float aerator_on_do_mg_l = 4.0f;
    float aerator_off_do_mg_l = 5.5f;
    float nh3_alarm_mg_l = 0.5f;
    float battery_low_v = 6.8f;
};

struct CrashWeights {
    float do_weight = 0.38f;
    float trend_weight = 0.22f;
    float nh3_weight = 0.25f;
    float temperature_weight = 0.05f;
    float time_weight = 0.10f;
};

constexpr int NH3_ANALOG_PIN = 5;

constexpr int I2C_SDA_PIN = 6;
constexpr int I2C_SCL_PIN = 7;

constexpr int TEMPERATURE_PIN = 4;

constexpr int AERATOR_RELAY_PIN = 0;
constexpr int DO_PUMP_RELAY_PIN = 1;

constexpr int GSM_TX_PIN = 21;
constexpr int GSM_RX_PIN = 20;

constexpr int SD_SCK_PIN = 10;
constexpr int SD_MISO_PIN = 19;
constexpr int SD_MOSI_PIN = 18;
constexpr int SD_CS_PIN = 3;

constexpr int BATTERY_ADS1115_CHANNEL = 2;
constexpr int DO_ADS1115_CHANNEL = 1;
constexpr int PH_ADS1115_P_CHANNEL = 0;
constexpr int PH_ADS1115_N_CHANNEL = 3;

constexpr float DO_SIM_MAX_MG_L = 12.0f;
constexpr float NH3_SIM_MAX_MG_L = 1.2f;
constexpr float PH_SIM_MIN = 5.0f;
constexpr float PH_SIM_MAX = 10.0f;
constexpr float BATTERY_SIM_MIN_V = 6.0f;
constexpr float BATTERY_SIM_MAX_V = 8.4f;

constexpr float DO_TREND_NORMALIZATION_MG_L_PER_MIN = 0.30f;
constexpr float HIGH_RISK_SCORE = 70.0f;
constexpr float LOW_RISK_SCORE = 45.0f;

constexpr bool AERATOR_FAIL_SAFE_ON = true;

} // namespace ponguard::config
