"""PondGuard M7.5 final hardware-simulation package generator.

Creates a reproducible design-freeze manifest from the validated M7.1-M7.4
artifacts. No claim of physical PCB ERC/DRC or vendor-certified SPICE is made.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
OUT = REPORTS / "m7_5"

REQUIRED = [
    "config/pinmap_m6_5.json",
    "hardware/bom/M6_7_BOM.csv",
    "wokwi/generated/diagram.json",
    "wokwi/generated/sketch.ino",
    "wokwi/generated/ads1115.chip.c",
    "wokwi/generated/ads1115.chip.json",
    "simulation/m7_2/electrical_sim.py",
    "simulation/m7_3/parametric_sweeps.py",
    "simulation/m7_4/transient_refinement.py",
    "hardware/do_afe/spice/do_tia_m7_2.cir",
    "hardware/power/spice/gsm_transient_reduced_order.cir",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        raise SystemExit("Missing required artifacts:\n" + "\n".join(missing))

    artifacts = []
    for rel in REQUIRED:
        p = ROOT / rel
        artifacts.append({
            "path": rel,
            "bytes": p.stat().st_size,
            "sha256": sha256(p),
        })

    manifest = {
        "milestone": "M7.5",
        "title": "Final Hardware Simulation Package & Design-Freeze Candidate",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "DESIGN_FREEZE_CANDIDATE",
        "scope": [
            "connection-level Wokwi hardware simulation",
            "electrical reference models",
            "parametric tolerance/boundary analysis",
            "worst-case transient refinement",
            "reproducible design assumptions and engineering flags",
        ],
        "validation_basis": {
            "m7_1": "user-verified Wokwi runtime + automated regression",
            "m7_2": "electrical reference simulation",
            "m7_3": "5000-sample parametric/Monte-Carlo sweeps",
            "m7_4": "GSM transient + battery sag worst-case refinement",
        },
        "freeze_decisions": {
            "gsm_bulk_cap_uF_candidate": 4700,
            "gsm_min_robust_cap_uF_modeled": 3300,
            "gsm_burst_assumption_A": 2.0,
            "gsm_burst_duration_ms": 1.0,
            "gsm_min_rail_v": 3.4,
            "battery_low_ocv_policy_v_range": [6.4, 6.8],
            "bms_continuous_rating_A_target": 5.0,
            "ads1115_address": "0x48",
            "nh3_mode": "qualitative",
            "aerator_fail_safe": "ON",
            "do_pump_fail_safe": "OFF",
        },
        "simulation_limits": [
            "Wokwi does not model the complete physical sensor chemistry.",
            "SEN0567 remains a qualitative gas-phase input; no universal dissolved-NH3 conversion is claimed.",
            "M7.4 regulator transient is reduced-order, not vendor-certified closed-loop SPICE.",
            "KiCad GUI ERC/DRC and PCB footprint verification are not claimed as completed here.",
            "Exact procurement-hold parts remain subject to physical package/vendor confirmation.",
        ],
        "open_holds": [
            "2S Li-ion BMS exact MPN / balancing topology",
            "5W PV panel exact MPN and measured Voc/Isc for fuse/TVS freeze",
            "SIM800L breakout exact revision and connector/level behavior",
            "outdoor keyed IP-rated connectors",
            "final actuator-driver transistor package/footprint",
        ],
        "artifacts": artifacts,
    }

    (OUT / "design_freeze_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    summary = [
        "PONDGUARD M7.5 — FINAL HARDWARE SIMULATION PACKAGE",
        "Status: DESIGN-FREEZE CANDIDATE",
        "",
        "Validated simulation stack:",
        "  M7.1  Wokwi connection-level hardware simulation",
        "  M7.2  electrical reference models",
        "  M7.3  5,000-sample parametric boundary sweeps",
        "  M7.4  worst-case GSM transient + battery sag refinement",
        "",
        "Freeze candidates:",
        "  GSM bulk capacitor candidate: 4,700 uF",
        "  Minimum modeled robust GSM bulk capacitance: 3,300 uF",
        "  Battery low-OCV policy: approximately 6.4–6.8 V",
        "  BMS continuous-current target: >=5 A",
        "  Aerator fail-safe: ON",
        "  DO circulation pump fail-safe: OFF",
        "  ADS1115 I2C address: 0x48",
        "  SEN0567 interpretation: qualitative only",
        "",
        "This package is NOT a claim of completed PCB fabrication release.",
        "KiCad GUI ERC/DRC, footprint checks, and procurement-hold MPN confirmation remain outside this simulation freeze.",
        "",
    ]
    (OUT / "DESIGN_FREEZE_SUMMARY.txt").write_text("\n".join(summary), encoding="utf-8")
    print((OUT / "DESIGN_FREEZE_SUMMARY.txt").read_text(encoding="utf-8"))
    print(f"Manifest: {OUT / 'design_freeze_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
