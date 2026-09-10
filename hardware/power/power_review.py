"""M6.7 power-review calculations for the frozen candidate architecture."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Rail:
    name: str
    vin_min: float
    vin_max: float
    vout: float
    current_a: float

RAILS = [
    Rail("5V_SYS", 6.0, 8.4, 5.0, 1.0),
    Rail("3V3", 6.0, 8.4, 3.3, 0.8),
    Rail("SIM800_4V", 6.0, 8.4, 4.0, 2.0),
]


def lmr51430_feedback(vout: float, rbot_ohm: float = 100_000.0) -> tuple[float, float]:
    vfb = 0.6
    rtop = rbot_ohm * (vout / vfb - 1.0)
    achieved = vfb * (1.0 + round(rtop, 0) / rbot_ohm)
    return round(rtop), achieved


def main() -> None:
    print("PondGuard M6.7 — pre-fabrication power review")
    for rail in RAILS:
        rtop, achieved = lmr51430_feedback(rail.vout)
        print(f"{rail.name}: {rtop:.0f} ohm / 100k -> {achieved:.3f} V")
    pack_wh = 7.4 * 4.4
    solar_upper_a = 5.0 / 8.4
    print(f"2S pack nominal energy: {pack_wh:.2f} Wh")
    print(f"5W panel ideal current at 8.4V: {solar_upper_a:.3f} A")
    print("SIM800 rail design target: 4.0 V, 2.0 A burst")

if __name__ == "__main__":
    main()
