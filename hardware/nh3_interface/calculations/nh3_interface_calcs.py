import math

R_SERIES = 1_000.0
C_FILTER = 100e-9
R_LOAD = 4_700.0
V_SENSOR = 3.3


def rc_cutoff_hz(r_ohm: float, c_f: float) -> float:
    return 1.0 / (2.0 * math.pi * r_ohm * c_f)


def load_current_ma(v: float, r: float) -> float:
    return (v / r) * 1000.0


if __name__ == "__main__":
    print("PondGuard M6.4 — NH3 interface calculations")
    print(f"1k/100nF input RC cutoff: {rc_cutoff_hz(R_SERIES, C_FILTER):.2f} Hz")
    print(f"4.7k load at 3.3V: {load_current_ma(V_SENSOR, R_LOAD):.3f} mA")
    print("Sensor current: <20 mA (vendor specification)")
    print("Quantitative dissolved-NH3 conversion: NOT implemented")
