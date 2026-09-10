import math

R = 8.31446261815324
F = 96485.33212


def nernst_slope_v_per_ph(temp_c: float) -> float:
    """Ideal Nernst magnitude S(T)=2.303RT/F in V/pH."""
    T = temp_c + 273.15
    return 2.303 * R * T / F


def differential_voltage_v(ph: float, temp_c: float) -> float:
    """Centered at pH 7; sign is conventional and must be confirmed on hardware."""
    return nernst_slope_v_per_ph(temp_c) * (7.0 - ph)


def bias_voltage_v(vcc: float = 3.3) -> float:
    return vcc / 2.0


def two_resistor_divider_current_a(vcc: float, r_top: float, r_bottom: float) -> float:
    return vcc / (r_top + r_bottom)


if __name__ == "__main__":
    print("PondGuard M6.3 — pH AFE calculations")
    for temp in (0.0, 25.0, 30.0, 40.0):
        s = nernst_slope_v_per_ph(temp)
        print(f"{temp:5.1f} C: {s*1000:.3f} mV/pH")
    for ph in (4.0, 7.0, 10.0):
        v = differential_voltage_v(ph, 25.0)
        print(f"25 C, pH={ph:.1f}: {v*1000:+.2f} mV")
    print(f"3.3V / 2 bias: {bias_voltage_v()*1000:.1f} mV")
    print(f"10k/10k divider current: {two_resistor_divider_current_a(3.3, 10000, 10000)*1e6:.1f} uA")
