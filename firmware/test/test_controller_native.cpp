#include <cassert>
#include <cmath>
#include "ponguard/controller.hpp"

using namespace ponguard;

static EnvironmentalSample sample(
    float do_mg_l,
    float nh3,
    float ph = 8.0f,
    float temp = 28.0f,
    float battery = 7.5f,
    uint32_t t = 0
) {
    EnvironmentalSample s{};
    s.dissolved_oxygen_mg_l = {do_mg_l, true, t};
    s.free_nh3_mg_l = {nh3, true, t};
    s.ph = {ph, true, t};
    s.temperature_c = {temp, true, t};
    s.battery_v = {battery, true, t};
    return s;
}

int main() {
    {
        Controller c;
        auto out = c.update(sample(7.2f, 0.05f, 8, 28, 7.5f, 0), 14.0f, true);
        assert(out.actuators.aerator == ActuatorState::OFF);
        assert(out.reason == DecisionReason::NORMAL ||
               out.reason == DecisionReason::HYSTERESIS_HOLD);
    }

    {
        Controller c;
        auto out = c.update(sample(3.5f, 0.10f, 8, 28, 7.5f, 0), 14.0f, true);
        assert(out.actuators.aerator == ActuatorState::ON);
        assert(out.reason == DecisionReason::DO_LOW);
    }

    {
        Controller c;
        auto out = c.update(sample(7.0f, 0.05f, 8, 28, 7.5f, 0), 14.0f, false);
        assert(out.actuators.aerator == ActuatorState::ON);
        assert(out.reason == DecisionReason::FAIL_SAFE_SENSOR_FAULT);
    }

    {
        Controller c;
        auto a = c.update(sample(5.0f, 0.1f, 8, 28, 7.5f, 0), 12.0f, true);
        auto b = c.update(sample(4.0f, 0.1f, 8, 28, 7.5f, 60000), 12.0f, true);
        (void)a;
        assert(b.do_trend_mg_l_per_min < 0.0f);
        assert(std::isfinite(b.crash_score));
    }

    return 0;
}
