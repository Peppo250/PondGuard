#ifdef ARDUINO

#include <Arduino.h>
#include <cmath>

#include "ponguard/arduino_hardware.hpp"
#include "ponguard/controller.hpp"

using namespace ponguard;

namespace {
ArduinoHardwareSensors sensors;
ArduinoActuators actuators;
Controller controller;
unsigned long last_sample_ms = 0;
}

void setup() {
    Serial.begin(115200);
    delay(500);

    sensors.begin();
    actuators.begin();

    Serial.println();
    Serial.println("=== PondGuard M6.5 ESP32-C3 Integration ===");
    Serial.println("Sense -> Interpret -> Predict -> Act");
}

void loop() {
    const unsigned long now = millis();

    if (now - last_sample_ms < 5000UL) {
        delay(5);
        return;
    }
    last_sample_ms = now;

    EnvironmentalSample sample = sensors.read();

    const bool valid =
        isFiniteValid(sample.dissolved_oxygen_mg_l) &&
        isFiniteValid(sample.free_nh3_mg_l) &&
        isFiniteValid(sample.ph) &&
        isFiniteValid(sample.temperature_c) &&
        isFiniteValid(sample.battery_v);

    const float simulation_hour = std::fmod(
        static_cast<float>(now) / 3600000.0f, 24.0f
    );

    ControllerOutput output =
        controller.update(sample, simulation_hour, valid);

    // Measurement-support pump scheduling remains outside the crash controller.
    output.actuators.do_circulation_pump =
        ((now / 1000UL) % 35UL) < 5UL
            ? ActuatorState::ON
            : ActuatorState::OFF;

    actuators.apply(output.actuators);

    Serial.printf(
        "DO=%.2f NH3=%.3f pH=%.2f T=%.2f V=%.2f score=%.1f trend=%.3f aerator=%d reason=%s\n",
        sample.dissolved_oxygen_mg_l.value,
        sample.free_nh3_mg_l.value,
        sample.ph.value,
        sample.temperature_c.value,
        sample.battery_v.value,
        output.crash_score,
        output.do_trend_mg_l_per_min,
        output.actuators.aerator == ActuatorState::ON,
        reasonToString(output.reason)
    );
}

#endif
