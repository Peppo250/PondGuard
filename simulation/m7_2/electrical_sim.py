"""M7.2 electrical reference simulations for PondGuard.

This module intentionally avoids pretending to be a transistor-level SPICE engine.
It reproduces the selected circuits with deterministic analytical/numerical models
and emits SPICE-compatible netlists for later execution with ngspice/LTspice.
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "m7_2"
OUT.mkdir(parents=True, exist_ok=True)

RF = 47_000.0
CF = 100e-9
R_PH_TOP = 10_000.0
R_PH_BOTTOM = 10_000.0
R_BAT_TOP = 10_000.0
R_BAT_BOTTOM = 3_300.0
NH3_R = 1_000.0
NH3_C = 100e-9
NH3_RLOAD = 100_000.0
VDD_ADC = 3.3
ADS_FSR_PH = 0.512


def nernst_slope(temp_c: float) -> float:
    R = 8.31446261815324
    F = 96485.33212
    return 2.303 * R * (temp_c + 273.15) / F


def csv_write(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def do_results() -> dict:
    tau = RF * CF
    fc = 1.0 / (2 * math.pi * RF * CF)
    rows = []
    for i_uA in [0.5, 1.0, 2.0, 3.0, 4.0]:
        rows.append({"current_uA": i_uA, "vout_mV": i_uA*1e-6*RF})
    # Unit-step response of the idealized TIA feedback pole.
    transient = []
    v_final = 0.141  # 3 uA through 47k
    for ms in [0, 0.1, 0.5, 1, 2, 5, 10, 20]:
        t = ms/1000.0
        v = v_final*(1-math.exp(-t/tau))
        transient.append({"time_ms": ms, "vout_V": v})
    csv_write(OUT/"do_tia_dc_sweep.csv", rows)
    csv_write(OUT/"do_tia_step_response.csv", transient)
    return {"rf_ohm":RF,"cf_f":CF,"tau_s":tau,"fc_hz":fc,"dc":rows,"step":transient}


def ph_results() -> dict:
    rows=[]
    for t in [0, 25, 30, 40]:
        s=nernst_slope(t)
        for ph in [4, 7, 10]:
            dv=s*(7-ph)
            rows.append({"temp_c":t,"ph":ph,"slope_mV_per_ph":s*1000,"diff_mV":dv*1000,"within_ads_fs_0p512":abs(dv)<=ADS_FSR_PH})
    csv_write(OUT/"ph_nernst_sweep.csv", rows)
    bias=3.3/2
    return {"bias_v":bias,"rows":rows,"ads_fsr_v":ADS_FSR_PH}


def nh3_results() -> dict:
    # The ADC-side RC is evaluated against the 100k input load used in the design note.
    r_eq = 1.0/(1.0/NH3_R + 1.0/NH3_RLOAD)
    fc = 1.0/(2*math.pi*r_eq*NH3_C)
    tau=r_eq*NH3_C
    # Pure RC step response, normalized to 1 V.
    rows=[]
    for us in [0, 10, 25, 50, 100, 250, 500, 1000]:
        t=us*1e-6
        rows.append({"time_us":us,"normalized_v":1-math.exp(-t/tau)})
    csv_write(OUT/"nh3_filter_step_response.csv", rows)
    fc_ideal = 1.0/(2*math.pi*NH3_R*NH3_C)
    return {"r_series_ohm":NH3_R,"r_load_ohm":NH3_RLOAD,"r_eq_ohm":r_eq,"c_f":NH3_C,"tau_s":tau,"fc_hz_loaded":fc,"fc_hz_ideal":fc_ideal,"step":rows}


def battery_results() -> dict:
    ratio=R_BAT_BOTTOM/(R_BAT_TOP+R_BAT_BOTTOM)
    rows=[]
    for vb in [6.0,6.8,7.4,8.4]:
        rows.append({"battery_v":vb,"adc_node_v":vb*ratio,"divider_current_mA":vb/(R_BAT_TOP+R_BAT_BOTTOM)*1000})
    csv_write(OUT/"battery_divider_sweep.csv", rows)
    return {"ratio":ratio,"rows":rows,"adc_max_v":VDD_ADC}


def power_results() -> dict:
    # Selected worst-case rail currents from M6.7. Efficiency is a scenario parameter,
    # not a component guarantee. This is explicitly a power-budget sensitivity study.
    rails=[("5V_SYS",5.0,1.0), ("3V3",3.3,0.8), ("SIM800_4V",4.0,2.0)]
    rows=[]
    for eta in [0.85,0.90,0.95]:
        for vin in [6.0,7.4,8.4]:
            pout=sum(v*i for _,v,i in rails)
            pin=pout/eta
            rows.append({"battery_v":vin,"efficiency":eta,"total_output_w":pout,"battery_input_w":pin,"battery_input_a":pin/vin})
    csv_write(OUT/"power_budget_sweep.csv", rows)
    return {"rails":rails,"rows":rows,"total_output_w":sum(v*i for _,v,i in rails)}


def gsm_cap_sizing() -> dict:
    # Battery-backed transient support calculation: deltaV = I*dt/C.
    rows=[]
    for c_uF in [220,470,1000,2200,4700,10000]:
        for ms in [0.1,0.5,1.0]:
            dv=2.0*(ms/1000)/(c_uF*1e-6)
            rows.append({"cap_uF":c_uF,"pulse_ms":ms,"delta_v_ideal":dv})
    csv_write(OUT/"gsm_capacitor_sizing.csv", rows)
    return {"assumed_pulse_current_a":2.0,"rows":rows,"formula":"dV = I*dt/C"}


def summary():
    result={"do_tia":do_results(),"ph":ph_results(),"nh3":nh3_results(),"battery_divider":battery_results(),"power":power_results(),"gsm_cap":gsm_cap_sizing()}
    (OUT/"m7_2_results.json").write_text(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    r=summary()
    print("PondGuard M7.2 electrical reference simulation")
    print(f"DO TIA: fc={r['do_tia']['fc_hz']:.2f} Hz, tau={r['do_tia']['tau_s']*1000:.3f} ms")
    print(f"pH: 25C slope={nernst_slope(25)*1000:.3f} mV/pH")
    print(f"NH3 input: fc={r['nh3']['fc_hz_ideal']:.2f} Hz ideal / {r['nh3']['fc_hz_loaded']:.2f} Hz loaded, tau={r['nh3']['tau_s']*1e6:.2f} us")
    print(f"Battery divider ratio={r['battery_divider']['ratio']:.6f}")
    print(f"Worst-case selected rail output power={r['power']['total_output_w']:.2f} W")
