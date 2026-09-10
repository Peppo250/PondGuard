#include "ponguard/sensor_sim.hpp"

namespace ponguard {

SimulatedSensorProvider::SimulatedSensorProvider(EnvironmentalSample sample)
    : sample_(sample) {}

EnvironmentalSample SimulatedSensorProvider::read() {
    return sample_;
}

void SimulatedSensorProvider::setSample(const EnvironmentalSample& sample) {
    sample_ = sample;
}

} // namespace ponguard
