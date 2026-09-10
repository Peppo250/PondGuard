from pathlib import Path
import csv
import math

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "hardware/ph_afe/calculations/ph_sweep.csv"

R = 8.31446261815324
F = 96485.33212
T = 25.0 + 273.15
S = 2.303 * R * T / F

rows = []
for ph in [0, 2, 4, 6, 7, 8, 10, 12, 14]:
    v = S * (7 - ph)
    rows.append({
        "temperature_C": 25,
        "pH": ph,
        "ideal_Nernst_mV_per_pH": round(S * 1000, 4),
        "VPH_DIFF_V": round(v, 6),
        "VPH_DIFF_mV": round(v * 1000, 3),
    })

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print(OUT)
