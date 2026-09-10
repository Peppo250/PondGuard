
from pathlib import Path
import csv
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_cn3791_is_not_used_as_2s_charger():
    text = (ROOT / "hardware/power/POWER_ARCHITECTURE.md").read_text()
    assert "single-cell" in text.lower()
    assert "CN3791" in text
    assert "must not be used" in text


def test_cn3722_and_pv_requirement_are_explicit():
    net = yaml.safe_load(
        (ROOT / "hardware/power/netlist/power_netlist.yaml").read_text()
    )
    assert net["blocks"]["charger"]["part"] == "CN3722"
    assert "2S Li-ion" in net["blocks"]["charger"]["battery"]


def test_gsm_peak_current_requirement_is_present():
    net = yaml.safe_load(
        (ROOT / "hardware/power/netlist/power_netlist.yaml").read_text()
    )
    assert net["blocks"]["gsm_regulator"]["peak_current_a"] >= 2.0


def test_preliminary_kicad_draft_exists():
    p = ROOT / "hardware/power/kicad/PondGuard_M6_1_power_draft.sch"
    assert p.exists()
    assert "NOT FOR FABRICATION" in p.read_text()


def test_bom_has_review_items():
    rows = list(csv.DictReader((ROOT / "hardware/bom/power_bom.csv").open()))
    statuses = {row["Status"] for row in rows}
    assert "REVIEW" in statuses
    assert "SELECT" in statuses
