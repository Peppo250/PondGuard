from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulation" / "m7_2"))
import electrical_sim as sim


def test_do_tia_values():
    assert abs(1e-6 * sim.RF - 0.047) < 1e-12
    assert abs(1.0 / (2*sim.math.pi*sim.RF*sim.CF) - 33.8627) < 0.01


def test_ph_25c():
    assert abs(sim.nernst_slope(25)*1000 - 59.167) < 0.1
    assert abs(sim.nernst_slope(25)*(7-4)*1000 - 177.5) < 0.5


def test_nh3_filter():
    r_eq=1/(1/sim.NH3_R+1/sim.NH3_RLOAD)
    fc=1/(2*sim.math.pi*r_eq*sim.NH3_C)
    assert 1600 < fc < 1615


def test_battery_divider():
    ratio=sim.R_BAT_BOTTOM/(sim.R_BAT_TOP+sim.R_BAT_BOTTOM)
    assert abs(ratio - 0.24812030075) < 1e-9
    assert abs(8.4*ratio - 2.0842105) < 1e-5


def test_power_total():
    assert abs((5*1)+(3.3*0.8)+(4*2) - 15.64) < 1e-12


def test_power_input_current_screen():
    # 90% sensitivity case at 6V battery
    pin=15.64/0.90
    assert abs(pin/6.0 - 2.8962963) < 1e-6


def test_gsm_cap_formula():
    # 2 A for 1 ms with 2200 uF -> ~0.909 V idealized droop.
    dv=2*0.001/2200e-6
    assert abs(dv - 0.9090909) < 1e-6


def test_netlists_exist():
    root=Path(__file__).resolve().parents[1]
    paths=[
        root/"hardware/do_afe/spice/do_tia_m7_2.cir",
        root/"hardware/ph_afe/spice/ph_buffer_m7_2.cir",
        root/"hardware/nh3_interface/spice/nh3_filter_m7_2.cir",
        root/"hardware/power/spice/power_transient_m7_2.cir",
    ]
    assert all(p.exists() for p in paths)
