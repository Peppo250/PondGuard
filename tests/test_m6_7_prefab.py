from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m6_7_docs_and_bom_exist():
    assert (ROOT / 'docs' / 'M6_7.md').exists()
    assert (ROOT / 'hardware' / 'bom' / 'M6_7_BOM.csv').exists()
    assert (ROOT / 'hardware' / 'power' / 'power_review.py').exists()


def test_power_regulator_candidates():
    text = (ROOT / 'config' / 'hardware.yaml').read_text()
    assert 'LMR51430XFDDCR' in text
    assert 'rail_sim800_4v' in text


def test_safety_invariants_preserved():
    text = (ROOT / 'config' / 'hardware.yaml').read_text()
    assert "aerator_safe_state: 'ON'" in text
    assert "do_circulation_pump" in text
