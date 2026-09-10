#pragma once
#include <cmath>
#include <cstdint>

enum class SimActuatorState { OFF, ON };
struct SimSample {
  float do_mg_l = 0;
  float nh3 = 0;
  float ph = 7;
  float temp_c = 28;
  float battery_v = 7.4f;
  uint32_t timestamp_ms = 0;
  bool valid = true;
};
struct SimOutput {
  SimActuatorState aerator = SimActuatorState::OFF;
  SimActuatorState pump = SimActuatorState::OFF;
  float score = 0;
  float trend = 0;
  const char *reason = "NORMAL";
};
class SimController {
 public:
  SimOutput update(const SimSample &s, float hour) {
    SimOutput o{};
    if (!s.valid) {
      aerator_on_ = true;
      o.aerator = SimActuatorState::ON;
      o.reason = "FAIL_SAFE_SENSOR_FAULT";
      updateTrend(s);
      return o;
    }
    updateTrend(s);
    const float do_risk = clamp((5.5f - s.do_mg_l) / 2.0f);
    const float trend_risk = clamp((-trend_) / 0.30f);
    const float nh3_risk = clamp(s.nh3 / 0.5f);
    const float temp_risk = clamp((s.temp_c - 30.0f) / 5.0f);
    const bool night = hour >= 18.0f || hour < 6.0f;
    const float time_risk = night ? 1.0f : 0.25f;
    o.score = 100.0f * (0.38f*do_risk + 0.22f*trend_risk + 0.25f*nh3_risk + 0.05f*temp_risk + 0.10f*time_risk);
    if (s.do_mg_l < 4.0f) { aerator_on_ = true; o.reason = "DO_LOW"; }
    else if (s.nh3 >= 0.5f && o.score >= 70.0f) { aerator_on_ = true; o.reason = "HIGH_COMBINED_RISK"; }
    else if (o.score >= 70.0f) { aerator_on_ = true; o.reason = "CRASH_SCORE_HIGH"; }
    else if (s.do_mg_l > 5.5f && o.score < 45.0f) { aerator_on_ = false; o.reason = "NORMAL"; }
    else { o.reason = "HYSTERESIS_HOLD"; }
    o.aerator = aerator_on_ ? SimActuatorState::ON : SimActuatorState::OFF;
    o.trend = trend_;
    return o;
  }
 private:
  bool aerator_on_ = true;
  float prev_do_ = 0;
  uint32_t prev_t_ = 0;
  bool have_prev_ = false;
  static float clamp(float x) { return x < 0 ? 0 : (x > 1 ? 1 : x); }
  void updateTrend(const SimSample &s) {
    trend_ = 0;
    if (have_prev_) {
      float dt = float(s.timestamp_ms - prev_t_) / 60000.0f;
      if (dt > 0) trend_ = (s.do_mg_l - prev_do_) / dt;
    }
    prev_do_ = s.do_mg_l;
    prev_t_ = s.timestamp_ms;
    have_prev_ = true;
  }
  float trend_ = 0;
};
