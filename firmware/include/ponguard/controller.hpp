#pragma once

#include "ponguard/sensors.hpp"
#include "ponguard/actuators.hpp"
#include "ponguard/config.hpp"

namespace ponguard {

enum class DecisionReason {
    NORMAL,
    DO_LOW,
    CRASH_SCORE_HIGH,
    HIGH_COMBINED_RISK,
    HYSTERESIS_HOLD,
    FAIL_SAFE_SENSOR_FAULT,
    BATTERY_LOW
};

struct ControllerOutput {
    ActuatorCommand actuators{};
    float crash_score{0.0f};
    float do_trend_mg_l_per_min{0.0f};
    DecisionReason reason{DecisionReason::NORMAL};
};

class Controller {
public:
    explicit Controller(
        config::ControlThresholds thresholds = {},
        config::CrashWeights weights = {}
    );

    ControllerOutput update(
        const EnvironmentalSample& sample,
        float time_hour,
        bool sensor_data_valid
    );

    void reset();

private:
    config::ControlThresholds thresholds_;
    config::CrashWeights weights_;
    bool aerator_on_{false};

    float previous_do_{0.0f};
    uint32_t previous_timestamp_ms_{0};
    bool have_previous_do_{false};

    float clamp01(float x) const;
};

const char* reasonToString(DecisionReason reason);

} // namespace ponguard
