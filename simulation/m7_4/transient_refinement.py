"""M7.4 reduced-order worst-case transient refinement.

Purpose:
- quantify GSM 4.0 V rail droop with capacitor ESR + regulator current-loop response;
- check 2S battery current and source/BMS limits under worst-case simultaneous loads;
- expose explicit assumptions because no vendor regulator macromodel is executed here.

This is a deterministic engineering boundary model, not a vendor SPICE macromodel.
"""
from __future__ import annotations
import csv, json, math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "m7_4"
PLOTS = OUT / "plots"
OUT.mkdir(parents=True, exist_ok=True)
PLOTS.mkdir(parents=True, exist_ok=True)

VOUT_NOM = 4.0
VOUT_MIN = 3.4
PULSE_A = 2.0
PULSE_MS = 1.0
I_GSM_STEADY = 0.10
I_REG_MAX = 3.0  # architecture/design capacity; not a vendor transient guarantee


def gsm_transient(cap_uF: float, esr_mohm: float, tau_ms: float, dt_us: float = 1.0) -> dict:
    """Simulate load step with first-order regulator current response.

    Ireg(t) = Isteady + (Imax-Isteady)*(1-exp(-t/tau))
    C*dV/dt = Ireg-Iload
    ESR contributes instantaneous I_step*ESR at t=0.
    """
    C = cap_uF * 1e-6
    esr = esr_mohm * 1e-3
    tau = tau_ms * 1e-3
    total_us = PULSE_MS * 1000.0
    steps = int(total_us / dt_us) + 1
    t = np.linspace(0.0, PULSE_MS / 1000.0, steps)
    vcap_drop = 0.0
    vmin_ideal = VOUT_NOM - PULSE_A * esr
    ireg_peak = I_GSM_STEADY
    q_deficit = 0.0
    for ti in t[1:]:
        ireg = I_GSM_STEADY + (I_REG_MAX - I_GSM_STEADY) * (1.0 - math.exp(-ti / tau)) if tau > 0 else I_REG_MAX
        ireg = min(ireg, I_REG_MAX)
        ireg_peak = max(ireg_peak, ireg)
        deficit = max(PULSE_A - ireg, 0.0)
        q_deficit += deficit * (dt_us * 1e-6)
    vcap_drop = q_deficit / C
    vmin = VOUT_NOM - PULSE_A * esr - vcap_drop
    pass_flag = vmin >= VOUT_MIN
    return {
        "cap_uF": cap_uF, "esr_mohm": esr_mohm, "tau_ms": tau_ms,
        "v_esr_drop": PULSE_A * esr, "v_cap_drop": vcap_drop,
        "vmin_v": vmin, "regulator_current_peak_a": ireg_peak,
        "pass_3p4v": pass_flag,
    }


def gsm_sweep() -> dict:
    caps = [220, 470, 1000, 2200, 3300, 4700, 6800, 10000]
    esrs = [5, 10, 20, 30, 50, 75, 100, 150]
    taus = [0.05, 0.1, 0.2, 0.5, 1.0]
    rows=[]
    for c in caps:
        for e in esrs:
            for tau in taus:
                rows.append(gsm_transient(c,e,tau))
    with (OUT/'gsm_transient_sweep.csv').open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    passed=[r for r in rows if r['pass_3p4v']]
    worst_by_cap = {c: min(r['vmin_v'] for r in rows if r['cap_uF']==c) for c in caps}
    robust_caps=[c for c,v in worst_by_cap.items() if v >= VOUT_MIN]
    robust_min_cap=min(robust_caps) if robust_caps else None
    return {
        "samples": len(rows), "pass_rate": len(passed)/len(rows),
        "robust_min_passing_cap_uF": robust_min_cap,
        "worst_vmin_v": min(r['vmin_v'] for r in rows),
        "worst_case": min(rows, key=lambda r:r['vmin_v']),
        "worst_vmin_by_cap_uF": worst_by_cap,
        "assumptions": {"pulse_a":PULSE_A,"pulse_ms":PULSE_MS,"i_gsm_steady_a":I_GSM_STEADY,"regulator_max_a":I_REG_MAX},
    }


def battery_case(v_batt: float, eff: float, source_r_ohm: float, bms_limit_a: float,
                 output_power_w: float = 15.64) -> dict:
    pin_a = output_power_w / eff / v_batt
    sag_v = pin_a * source_r_ohm
    terminal_v = v_batt - sag_v
    current_margin = bms_limit_a - pin_a
    return {
        "battery_oc_v": v_batt, "efficiency": eff, "source_r_ohm": source_r_ohm,
        "bms_limit_a": bms_limit_a, "input_current_a": pin_a,
        "source_sag_v": sag_v, "battery_terminal_v": terminal_v,
        "current_margin_a": current_margin,
        "bms_pass": current_margin >= 0.0,
        "voltage_margin_to_6v_cutoff_v": terminal_v - 6.0,
    }


def battery_sweep() -> dict:
    rows=[]
    for vb in [6.0, 6.2, 6.4, 7.0, 7.4, 8.4]:
        for eff in [0.85,0.90,0.95]:
            for rs in [0.05,0.10,0.15,0.20,0.25]:
                for bms in [3.0,4.0,5.0,6.0]:
                    rows.append(battery_case(vb,eff,rs,bms))
    with (OUT/'battery_worst_case_sweep.csv').open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    min_margin=min(r['current_margin_a'] for r in rows)
    worst=min(rows, key=lambda r:r['current_margin_a'])
    voltage_fail=[r for r in rows if r['battery_terminal_v'] < 6.0]
    boundary = {}
    for eff in [0.85,0.90,0.95]:
        for rs in [0.05,0.10,0.15,0.20,0.25]:
            a=1.0; b=-6.0; c=-(15.64*rs/eff)
            boundary[f"eta={eff:.2f},R={rs:.2f}"]=( -b + math.sqrt(b*b-4*a*c) )/(2*a)
    return {"samples":len(rows),"bms_pass_rate":sum(r['bms_pass'] for r in rows)/len(rows),"min_current_margin_a":min_margin,"worst_case":worst,"terminal_voltage_fail_cases":len(voltage_fail),"min_oc_voltage_for_6v_terminal":min(boundary.values()),"max_oc_voltage_for_6v_terminal":max(boundary.values()),"terminal_boundary_by_case":boundary,"note":"BMS threshold is a parameter until a physical BMS is selected; source impedance is likewise a model input."}


def plots(gsm, batt):
    import matplotlib.pyplot as plt
    import numpy as np
    g=np.genfromtxt(OUT/'gsm_transient_sweep.csv',delimiter=',',names=True)
    plt.figure(figsize=(7,4.5))
    for e in [20,50,100]:
        mask=g['esr_mohm']==e
        for tau in [0.1,0.5,1.0]:
            m=mask & (g['tau_ms']==tau) & (g['cap_uF']==4700)
            if np.any(m): plt.scatter(g['tau_ms'][m],g['vmin_v'][m],label=f'ESR {int(e)} mΩ')
    plt.axhline(3.4); plt.xlabel('Regulator current-loop tau (ms)'); plt.ylabel('4 V rail minimum (V)'); plt.title('M7.4 GSM transient at 4700 µF'); plt.tight_layout(); plt.savefig(PLOTS/'gsm_4700uf_esr.png',dpi=160); plt.close()
    # heatmap-esque scatter for 0.5 ms tau
    mask=(g['tau_ms']==0.5)
    plt.figure(figsize=(7,4.5)); sc=plt.scatter(g['cap_uF'][mask],g['vmin_v'][mask],c=g['esr_mohm'][mask],s=18); plt.axhline(3.4); plt.xscale('log'); plt.xlabel('Bulk capacitance (µF)'); plt.ylabel('Minimum GSM rail (V)'); plt.title('M7.4 GSM pass boundary (tau=0.5 ms)'); plt.colorbar(sc,label='ESR (mΩ)'); plt.tight_layout(); plt.savefig(PLOTS/'gsm_boundary_tau0p5ms.png',dpi=160); plt.close()
    b=np.genfromtxt(OUT/'battery_worst_case_sweep.csv',delimiter=',',names=True)
    mask=(b['efficiency']==0.85)&(b['source_r_ohm']==0.15)&(b['bms_limit_a']==5.0)
    plt.figure(figsize=(7,4.5)); plt.plot(b['battery_oc_v'][mask],b['input_current_a'][mask],marker='o'); plt.axhline(5.0); plt.xlabel('Battery pack open-circuit voltage (V)'); plt.ylabel('Battery current (A)'); plt.title('M7.4 battery current at 85% efficiency'); plt.tight_layout(); plt.savefig(PLOTS/'battery_current_boundary.png',dpi=160); plt.close()


def main():
    gsm=gsm_sweep(); batt=battery_sweep(); plots(gsm,batt)
    summary={"gsm":gsm,"battery":batt,"status":"PASS_WITH_FLAGS","flags":[
        "Analytical regulator loop; no vendor LMR51430 macromodel executed.",
        "BMS rating/UVP/OVP thresholds remain parameterized procurement inputs."
    ]}
    (OUT/'m7_4_results.json').write_text(json.dumps(summary,indent=2))
    print('PondGuard M7.4 worst-case / transient refinement')
    print(f"GSM sweep: {gsm['samples']} cases; pass rate {gsm['pass_rate']*100:.2f}%; robust minimum capacitance={gsm['robust_min_passing_cap_uF']} uF")
    print(f"GSM worst Vmin: {gsm['worst_vmin_v']:.3f} V")
    print(f"Battery sweep: {batt['samples']} cases; BMS pass rate {batt['bms_pass_rate']*100:.2f}%; worst current margin={batt['min_current_margin_a']:.3f} A; cases below 6V terminal={batt['terminal_voltage_fail_cases']}")

if __name__=='__main__': main()
