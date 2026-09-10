import math

RF_OHM = 47_000.0
CF_F = 100e-9

def tia_voltage(current_uA: float) -> float:
    return current_uA * 1e-6 * RF_OHM

def feedback_pole_hz() -> float:
    return 1.0 / (2.0 * math.pi * RF_OHM * CF_F)

def ads1115_lsb_v(full_scale_single_sided_v: float) -> float:
    # Equivalent LSB for a differential full-scale span of 2*FSR.
    return (2.0 * full_scale_single_sided_v) / 65536.0

if __name__ == "__main__":
    print("PondGuard M6.2 — DO AFE baseline")
    for current in (1.0, 2.0, 3.0):
        print(f"{current:.1f} uA -> {tia_voltage(current)*1000:.1f} mV")
    print(f"feedback pole -> {feedback_pole_hz():.2f} Hz")
    for fsr in (0.256, 0.512, 1.024, 2.048):
        print(f"ADS1115 ±{fsr:.3f} V -> {ads1115_lsb_v(fsr)*1e6:.2f} uV/LSB")
