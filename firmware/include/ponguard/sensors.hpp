#pragma once

#include <cstdint>
#include <cmath>

namespace ponguard {

struct SensorReading {
    float value{};
    bool valid{false};
    uint32_t timestamp_ms{0};
};

struct EnvironmentalSample {
    SensorReading dissolved_oxygen_mg_l;
    SensorReading free_nh3_mg_l;
    SensorReading ph;
    SensorReading temperature_c;
    SensorReading battery_v;
};

class SensorProvider {
public:
    virtual ~SensorProvider() = default;
    virtual EnvironmentalSample read() = 0;
};

inline bool isFiniteValid(const SensorReading& r) {
    return r.valid && std::isfinite(r.value);
}

} // namespace ponguard
