from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "hardware/do_afe/calculations/do_tia_sweep.csv"

rf = 47000.0
rows = []
for current_uA in [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4]:
    v = current_uA * 1e-6 * rf
    rows.append({
        "probe_current_uA": current_uA,
        "tia_output_V": round(v, 6),
        "tia_output_mV": round(v * 1000, 3),
    })

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(OUT)
