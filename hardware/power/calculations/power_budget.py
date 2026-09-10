from dataclasses import dataclass


@dataclass(frozen=True)
class PowerAssumptions:
    solar_w: float = 5.0
    battery_nominal_v: float = 7.4
    battery_capacity_ah: float = 4.4
    system_efficiency: float = 0.80

    # Illustrative loads for budgeting; these are NOT measured values.
    esp32_3v3_w: float = 0.15
    analog_3v3_w: float = 0.10
    sensors_3v3_w: float = 0.10
    gsm_avg_w: float = 0.20
    gsm_peak_w: float = 8.0
    pump_w: float = 0.50

    gsm_regulator_v: float = 4.0
    gsm_peak_a: float = 2.0


def battery_energy_wh(a: PowerAssumptions) -> float:
    return a.battery_nominal_v * a.battery_capacity_ah


def theoretical_charge_current_a(a: PowerAssumptions) -> float:
    # Average current at nominal battery voltage if all PV power reached battery.
    return a.solar_w / 8.4


def practical_charge_current_a(a: PowerAssumptions) -> float:
    return theoretical_charge_current_a(a) * a.system_efficiency


def gsm_peak_power_w(a: PowerAssumptions) -> float:
    return a.gsm_regulator_v * a.gsm_peak_a


def dc_load_power_w(a: PowerAssumptions) -> float:
    return (
        a.esp32_3v3_w
        + a.analog_3v3_w
        + a.sensors_3v3_w
        + a.gsm_avg_w
        + a.pump_w
    )


if __name__ == "__main__":
    a = PowerAssumptions()

    print("PondGuard M6.1 — illustrative power budget")
    print(f"Battery nominal energy: {battery_energy_wh(a):.2f} Wh")
    print(f"Theoretical 8.4 V charge current from 5 W PV: {theoretical_charge_current_a(a):.3f} A")
    print(f"Illustrative 80% system charging current: {practical_charge_current_a(a):.3f} A")
    print(f"GSM peak power at 4.0 V / 2 A: {gsm_peak_power_w(a):.2f} W")
    print(f"Illustrative non-peak DC load: {dc_load_power_w(a):.2f} W")
