"""M7.3 deterministic worst-case and Monte-Carlo hardware sweeps.

These are engineering sensitivity models, not vendor-certified SPICE results.
Each domain preserves the M6.7 nominal topology and perturbs passive values,
temperature, battery voltage, and GSM pulse assumptions.
"""
from __future__ import annotations
import csv, json, math, random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "m7_3"
PLOTS = OUT / "plots"
OUT.mkdir(parents=True, exist_ok=True); PLOTS.mkdir(exist_ok=True)

N = 5000
SEED = 7301
rng = random.Random(SEED)

# Nominal M6.7/M7.2 values
RF=47_000.0; CF=100e-9
NH3_R=1_000.0; NH3_C=100e-9; NH3_LOAD=100_000.0
RB_TOP=10_000.0; RB_BOTTOM=3_300.0
ADS_FSR=0.512; VDD=3.3
R_PH_TOP=10_000.0; R_PH_BOTTOM=10_000.0


def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def qnormal(rng, nominal, tol, n):
    return [nominal*(1+rng.uniform(-tol,tol)) for _ in range(n)]


def nernst(temp_c):
    return 2.303*8.31446261815324*(temp_c+273.15)/96485.33212


def do_sweep():
    rows=[]
    for _ in range(N):
        rf=RF*rng.uniform(.95,1.05); cf=CF*rng.uniform(.95,1.05)
        fc=1/(2*math.pi*rf*cf); gain=rf
        v3=gain*3e-6
        rows.append({'rf_ohm':rf,'cf_f':cf,'fc_hz':fc,'vout_3uA_mV':v3*1000,'fc_pass':29.0<=fc<=39.0,'gain_pass':0.04465<=gain/1e6<=0.04935})
    write_csv(OUT/'do_tia_monte_carlo.csv', rows)
    return summarize(rows, ['fc_hz','vout_3uA_mV']) | {'pass_rate':sum(r['fc_pass'] and r['gain_pass'] for r in rows)/N}


def ph_sweep():
    rows=[]
    for t in range(-10,51,5):
        s=nernst(t)
        for ph in [4,5,6,7,8,9,10]:
            dv=s*(7-ph)
            rows.append({'temp_c':t,'ph':ph,'slope_mV_per_ph':s*1000,'diff_mV':dv*1000,'abs_diff_mV':abs(dv)*1000,'adc_range_pass':abs(dv)<=ADS_FSR})
    write_csv(OUT/'ph_temperature_boundary.csv', rows)
    return {'min_slope_mV_per_ph':min(r['slope_mV_per_ph'] for r in rows),'max_slope_mV_per_ph':max(r['slope_mV_per_ph'] for r in rows),'max_abs_diff_mV':max(r['abs_diff_mV'] for r in rows),'all_pass':all(r['adc_range_pass'] for r in rows)}


def nh3_sweep():
    rows=[]
    for _ in range(N):
        r=NH3_R*rng.uniform(.95,1.05); c=NH3_C*rng.uniform(.95,1.05); load=NH3_LOAD*rng.uniform(.95,1.05)
        req=1/(1/r+1/load); fc=1/(2*math.pi*req*c)
        rows.append({'r_series_ohm':r,'c_f':c,'r_load_ohm':load,'fc_hz':fc,'fc_pass':1400<=fc<=1800})
    write_csv(OUT/'nh3_filter_monte_carlo.csv', rows)
    return summarize(rows,['fc_hz']) | {'pass_rate':sum(r['fc_pass'] for r in rows)/N}


def battery_sweep():
    rows=[]
    for _ in range(N):
        rt=RB_TOP*rng.uniform(.99,1.01); rb=RB_BOTTOM*rng.uniform(.99,1.01); vb=rng.uniform(6.0,8.4)
        ratio=rb/(rt+rb); vadc=vb*ratio
        rows.append({'battery_v':vb,'r_top_ohm':rt,'r_bottom_ohm':rb,'ratio':ratio,'adc_v':vadc,'adc_pass':vadc<=3.0})
    write_csv(OUT/'battery_divider_monte_carlo.csv', rows)
    return summarize(rows,['ratio','adc_v']) | {'pass_rate':sum(r['adc_pass'] for r in rows)/N}


def power_sweep():
    rows=[]
    rails=[('5V',5.0,1.0),('3V3',3.3,.8),('GSM4V',4.0,2.0)]
    for eta in [.85,.90,.95]:
      for vb in [6.0,6.4,7.0,7.4,8.0,8.4]:
        pout=sum(v*i for _,v,i in rails); pin=pout/eta; ib=pin/vb
        rows.append({'battery_v':vb,'efficiency':eta,'output_power_w':pout,'battery_input_power_w':pin,'battery_input_current_a':ib,'rail_current_pass':all(i<3 for _,_,i in rails)})
    write_csv(OUT/'power_worst_case_sweep.csv', rows)
    return {'output_power_w':sum(v*i for _,v,i in rails),'max_input_current_a':max(r['battery_input_current_a'] for r in rows),'all_rail_current_pass':all(r['rail_current_pass'] for r in rows),'min_battery_v':6.0}


def gsm_sweep():
    rows=[]
    for cap in [470,1000,2200,3300,4700,6800,10000]:
      for ms in [.1,.25,.5,1.0,2.0]:
        dv=2*ms/1000/(cap*1e-6); vmin=4.0-dv
        rows.append({'cap_uF':cap,'pulse_ms':ms,'ideal_droop_v':dv,'vmin_ideal_v':vmin,'pass_3p4v':vmin>=3.4})
    write_csv(OUT/'gsm_cap_boundary.csv', rows)
    # Minimum capacitance for idealized 2 A pulse while staying >=3.4 V from 4.0 V.
    required=2*.001/(4.0-3.4)
    return {'required_cap_uF_for_1ms_3p4v':required*1e6,'note':'Ideal capacitor-only bound; regulator ESR/control-loop dynamics are not modeled.'}


def summarize(rows, keys):
    out={}
    for k in keys:
        vals=[r[k] for r in rows]; out[k]={'min':min(vals),'max':max(vals),'mean':sum(vals)/len(vals)}
    return out


def plots():
    import matplotlib.pyplot as plt
    import numpy as np
    # DO histogram
    data=np.genfromtxt(OUT/'do_tia_monte_carlo.csv',delimiter=',',names=True)
    plt.figure(figsize=(7,4.5)); plt.hist(data['fc_hz'],bins=40); plt.axvline(33.86); plt.xlabel('DO TIA cutoff frequency (Hz)'); plt.ylabel('Count'); plt.title('M7.3 DO TIA tolerance sweep'); plt.tight_layout(); plt.savefig(PLOTS/'do_tia_fc.png',dpi=160); plt.close()
    # NH3 histogram
    data=np.genfromtxt(OUT/'nh3_filter_monte_carlo.csv',delimiter=',',names=True)
    plt.figure(figsize=(7,4.5)); plt.hist(data['fc_hz'],bins=40); plt.axvline(1591.55); plt.xlabel('NH3 filter loaded cutoff (Hz)'); plt.ylabel('Count'); plt.title('M7.3 NH3 RC tolerance sweep'); plt.tight_layout(); plt.savefig(PLOTS/'nh3_fc.png',dpi=160); plt.close()
    # pH envelope
    ph=np.genfromtxt(OUT/'ph_temperature_boundary.csv',delimiter=',',names=True)
    temps=np.unique(ph['temp_c'])
    plt.figure(figsize=(7,4.5))
    for p in [4,7,10]:
      y=ph['diff_mV'][ph['ph']==p]; x=ph['temp_c'][ph['ph']==p]; plt.plot(x,y,label=f'pH {int(p)}')
    plt.axhline(512); plt.axhline(-512); plt.xlabel('Temperature (deg C)'); plt.ylabel('Differential pH voltage (mV)'); plt.title('M7.3 pH temperature envelope'); plt.legend(); plt.tight_layout(); plt.savefig(PLOTS/'ph_temperature_envelope.png',dpi=160); plt.close()
    # battery boundary
    bat=np.genfromtxt(OUT/'battery_divider_monte_carlo.csv',delimiter=',',names=True)
    plt.figure(figsize=(7,4.5)); plt.scatter(bat['battery_v'],bat['adc_v'],s=2,alpha=.15); plt.axhline(3.0); plt.xlabel('Battery pack voltage (V)'); plt.ylabel('ADC divider node (V)'); plt.title('M7.3 battery-divider tolerance sweep'); plt.tight_layout(); plt.savefig(PLOTS/'battery_divider.png',dpi=160); plt.close()


def main():
    results={'seed':SEED,'samples':N,'do_tia':do_sweep(),'ph':ph_sweep(),'nh3':nh3_sweep(),'battery':battery_sweep(),'power':power_sweep(),'gsm':gsm_sweep()}
    plots()
    (OUT/'m7_3_results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print('PondGuard M7.3 parametric / boundary analysis')
    print(f"DO TIA fc range: {results['do_tia']['fc_hz']['min']:.2f}-{results['do_tia']['fc_hz']['max']:.2f} Hz; pass rate {results['do_tia']['pass_rate']*100:.2f}%")
    print(f"pH max |dV|: {results['ph']['max_abs_diff_mV']:.2f} mV; ADC range pass={results['ph']['all_pass']}")
    print(f"NH3 fc range: {results['nh3']['fc_hz']['min']:.2f}-{results['nh3']['fc_hz']['max']:.2f} Hz; pass rate {results['nh3']['pass_rate']*100:.2f}%")
    print(f"Battery ADC max: {results['battery']['adc_v']['max']:.3f} V; pass rate {results['battery']['pass_rate']*100:.2f}%")
    print(f"Max battery input current in rail sensitivity: {results['power']['max_input_current_a']:.3f} A")
    print(f"Ideal GSM capacitance bound for 2A/1ms, 4.0->3.4V: {results['gsm']['required_cap_uF_for_1ms_3p4v']:.0f} uF")

if __name__=='__main__': main()
