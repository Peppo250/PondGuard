#ifndef ARDUINO

#include <iostream>
#include "ponguard/controller.hpp"

int main() {
    using namespace ponguard;

    Controller controller;

    EnvironmentalSample s{};
    s.dissolved_oxygen_mg_l = {7.0f, true, 0};
    s.free_nh3_mg_l = {0.05f, true, 0};
    s.ph = {8.0f, true, 0};
    s.temperature_c = {28.0f, true, 0};
    s.battery_v = {7.5f, true, 0};

    auto out = controller.update(s, 14.0f, true);

    std::cout << "M4 native controller smoke test\n";
    std::cout << "score=" << out.crash_score << "\n";
    std::cout << "aerator="
              << (out.actuators.aerator == ActuatorState::ON ? "ON" : "OFF")
              << "\n";
    std::cout << "reason=" << reasonToString(out.reason) << "\n";
    return 0;
}

#endif
