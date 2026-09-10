from pathlib import Path
import json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def run():
    subprocess.run([sys.executable, str(ROOT/'simulation/m7_3/parametric_sweeps.py')],check=True)

def test_results_exist_and_pass():
    run(); p=ROOT/'reports/m7_3/m7_3_results.json'; assert p.exists()
    r=json.loads(p.read_text())
    assert r['do_tia']['pass_rate'] == 1.0
    assert r['ph']['all_pass'] is True
    assert r['nh3']['pass_rate'] == 1.0
    assert r['battery']['pass_rate'] == 1.0
    assert r['power']['all_rail_current_pass'] is True
    assert 3300 < r['gsm']['required_cap_uF_for_1ms_3p4v'] < 3400

def test_expected_reports():
    for name in ['do_tia_monte_carlo.csv','ph_temperature_boundary.csv','nh3_filter_monte_carlo.csv','battery_divider_monte_carlo.csv','power_worst_case_sweep.csv','gsm_cap_boundary.csv']:
        assert (ROOT/'reports/m7_3'/name).exists()
    for name in ['do_tia_fc.png','nh3_fc.png','ph_temperature_envelope.png','battery_divider.png']:
        assert (ROOT/'reports/m7_3/plots'/name).exists()
