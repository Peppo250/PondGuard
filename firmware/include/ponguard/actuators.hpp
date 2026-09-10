#pragma once

namespace ponguard {

enum class ActuatorState {
    OFF,
    ON
};

struct ActuatorCommand {
    ActuatorState aerator{ActuatorState::OFF};
    ActuatorState do_circulation_pump{ActuatorState::OFF};
};

class ActuatorProvider {
public:
    virtual ~ActuatorProvider() = default;
    virtual void apply(const ActuatorCommand& command) = 0;
};

} // namespace ponguard
