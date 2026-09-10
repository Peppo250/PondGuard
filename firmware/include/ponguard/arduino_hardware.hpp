#pragma once

#ifdef ARDUINO

#include "ponguard/sensors.hpp"

namespace ponguard {

class ArduinoHardwareSensors : public SensorProvider {
public:
    ArduinoHardwareSensors();
    void begin();
    EnvironmentalSample read() override;

private:
    EnvironmentalSample last_{};
};

class ArduinoActuators : public ActuatorProvider {
public:
    ArduinoActuators();
    void begin();
    void apply(const ActuatorCommand& command) override;
};

} // namespace ponguard

#endif
