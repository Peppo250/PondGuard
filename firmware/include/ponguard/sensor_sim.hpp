#pragma once

#include "ponguard/sensors.hpp"

namespace ponguard {

class SimulatedSensorProvider : public SensorProvider {
public:
    explicit SimulatedSensorProvider(EnvironmentalSample sample = {});
    EnvironmentalSample read() override;
    void setSample(const EnvironmentalSample& sample);

private:
    EnvironmentalSample sample_{};
};

} // namespace ponguard
