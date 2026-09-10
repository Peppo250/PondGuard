from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from simulation.m7_4.transient_refinement import gsm_transient, gsm_sweep, battery_case, battery_sweep

def test_gsm_esr_and_cap_are_modeled():
    a=gsm_transient(2200,100,1.0)
    b=gsm_transient(4700,20,0.5)
    assert a['v_esr_drop'] > b['v_esr_drop']
    assert b['vmin_v'] > a['vmin_v']

def test_4700uf_typical_case_passes():
    r=gsm_transient(4700,20,0.5)
    assert r['vmin_v'] >= 3.4

def test_2200uf_pessimistic_case_fails():
    r=gsm_transient(2200,150,1.0)
    assert r['vmin_v'] < 3.4

def test_bms_five_amp_has_margin_at_nominal_case():
    r=battery_case(7.4,0.90,0.10,5.0)
    assert r['input_current_a'] < 5.0

def test_bms_three_amp_flags_low_voltage_worst_case():
    r=battery_case(6.0,0.85,0.15,3.0)
    assert not r['bms_pass']

def test_sweep_writes_expected_cases(tmp_path):
    gsm=gsm_sweep(); batt=battery_sweep()
    assert gsm['samples'] == 8*8*5
    assert batt['samples'] == 6*3*5*4
    assert gsm['robust_min_passing_cap_uF'] == 3300
    assert batt['min_current_margin_a'] < 0
    assert batt['terminal_voltage_fail_cases'] > 0
    assert batt['max_oc_voltage_for_6v_terminal'] > 6.0

def test_results_disclose_model_limits():
    p=Path(__file__).resolve().parents[1]/'docs'/'M7_4.md'
    text=p.read_text()
    assert 'not a vendor-certified' in text
    assert 'BMS' in text
