#include "ponguard/controller.hpp"
#include <cmath>

namespace ponguard {

Controller::Controller(
    config::ControlThresholds thresholds,
    config::CrashWeights weights
) : thresholds_(thresholds), weights_(weights) {}

float Controller::clamp01(float x) const {
    if (x < 0.0f) return 0.0f;
    if (x > 1.0f) return 1.0f;
    return x;
}

ControllerOutput Controller::update(
    const EnvironmentalSample& sample,
    float time_hour,
    bool sensor_data_valid
) {
    ControllerOutput out{};

    float trend = 0.0f;
    if (have_previous_do_) {
        const float dt_min =
            static_cast<float>(sample.dissolved_oxygen_mg_l.timestamp_ms - previous_timestamp_ms_) / 60000.0f;
        if (dt_min > 0.0f) {
            trend = (sample.dissolved_oxygen_mg_l.value - previous_do_) / dt_min;
        }
    }
    previous_do_ = sample.dissolved_oxygen_mg_l.value;
    previous_timestamp_ms_ = sample.dissolved_oxygen_mg_l.timestamp_ms;
    have_previous_do_ = true;
    out.do_trend_mg_l_per_min = trend;

    if (!sensor_data_valid) {
        aerator_on_ = config::AERATOR_FAIL_SAFE_ON;
        out.actuators.aerator = aerator_on_ ? ActuatorState::ON : ActuatorState::OFF;
        out.reason = DecisionReason::FAIL_SAFE_SENSOR_FAULT;
        return out;
    }

    const float do_risk =
        clamp01((thresholds_.aerator_off_do_mg_l -
                 sample.dissolved_oxygen_mg_l.value) / 2.0f);

    const float trend_risk =
        clamp01((-trend) / config::DO_TREND_NORMALIZATION_MG_L_PER_MIN);

    const float nh3_risk =
        clamp01(sample.free_nh3_mg_l.value / thresholds_.nh3_alarm_mg_l);

    const float temp_risk =
        clamp01((sample.temperature_c.value - 30.0f) / 5.0f);

    const bool night = (time_hour >= 18.0f || time_hour < 6.0f);
    const float time_risk = night ? 1.0f : 0.25f;

    out.crash_score = 100.0f * (
        weights_.do_weight * do_risk +
        weights_.trend_weight * trend_risk +
        weights_.nh3_weight * nh3_risk +
        weights_.temperature_weight * temp_risk +
        weights_.time_weight * time_risk
    );

    if (sample.battery_v.valid &&
        sample.battery_v.value < thresholds_.battery_low_v) {
        out.reason = DecisionReason::BATTERY_LOW;
        // Battery warning alone does not force the aerator off.
    }

    if (sample.dissolved_oxygen_mg_l.value < thresholds_.aerator_on_do_mg_l) {
        aerator_on_ = true;
        out.reason = DecisionReason::DO_LOW;
    } else if (
        sample.free_nh3_mg_l.value >= thresholds_.nh3_alarm_mg_l &&
        out.crash_score >= config::HIGH_RISK_SCORE
    ) {
        aerator_on_ = true;
        out.reason = DecisionReason::HIGH_COMBINED_RISK;
    } else if (out.crash_score >= config::HIGH_RISK_SCORE) {
        aerator_on_ = true;
        out.reason = DecisionReason::CRASH_SCORE_HIGH;
    } else if (
        sample.dissolved_oxygen_mg_l.value > thresholds_.aerator_off_do_mg_l &&
        out.crash_score < config::LOW_RISK_SCORE
    ) {
        aerator_on_ = false;
        if (out.reason != DecisionReason::BATTERY_LOW) {
            out.reason = DecisionReason::NORMAL;
        }
    } else {
        if (out.reason != DecisionReason::BATTERY_LOW) {
            out.reason = DecisionReason::HYSTERESIS_HOLD;
        }
    }

    out.actuators.aerator = aerator_on_ ? ActuatorState::ON : ActuatorState::OFF;
    return out;
}

void Controller::reset() {
    aerator_on_ = false;
    previous_do_ = 0.0f;
    previous_timestamp_ms_ = 0;
    have_previous_do_ = false;
}

const char* reasonToString(DecisionReason reason) {
    switch (reason) {
        case DecisionReason::NORMAL: return "NORMAL";
        case DecisionReason::DO_LOW: return "DO_LOW";
        case DecisionReason::CRASH_SCORE_HIGH: return "CRASH_SCORE_HIGH";
        case DecisionReason::HIGH_COMBINED_RISK: return "HIGH_COMBINED_RISK";
        case DecisionReason::HYSTERESIS_HOLD: return "HYSTERESIS_HOLD";
        case DecisionReason::FAIL_SAFE_SENSOR_FAULT: return "FAIL_SAFE_SENSOR_FAULT";
        case DecisionReason::BATTERY_LOW: return "BATTERY_LOW";
    }
    return "UNKNOWN";
}

} // namespace ponguard
