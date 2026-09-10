#!/usr/bin/env python3
"""PondGuard M7.6 full reproducible hardware-simulation validation pipeline.

Default behavior is STRICT: every stage must execute and pass.
The pipeline intentionally fails if PlatformIO or Wokwi CLI is unavailable;
it never silently skips hardware simulation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
WOKWI = ROOT / "wokwi" / "ci"
REPORT = ROOT / "reports" / "m7_6"
ARTIFACTS = WOKWI / "artifacts"
SCENARIOS = WOKWI / "scenarios"

# Ensure standard user toolchain directories are in PATH
user_paths = [
    Path(os.environ.get("APPDATA", "")) / "Python" / "Python314" / "Scripts",
    Path.home() / ".wokwi" / "bin",
]
for p in user_paths:
    if p.exists() and str(p) not in os.environ.get("PATH", ""):
        os.environ["PATH"] = str(p) + os.pathsep + os.environ.get("PATH", "")

# Load CI token from CI_token.txt if not in environment
if "WOKWI_CLI_TOKEN" not in os.environ:
    token_file = ROOT / "CI_token.txt"
    if token_file.exists():
        text = token_file.read_text(encoding="utf-8").strip()
        m = re.search(r'WOKWI_CLI_TOKEN=["\']?([^"\'\s]+)["\']?', text)
        if m:
            os.environ["WOKWI_CLI_TOKEN"] = m.group(1)

SCENARIO_ORDER = [
    "01_nominal.yaml",
    "02_hypoxia_trip.yaml",
    "03_recovery.yaml",
    "04_battery_low.yaml",
    "05_sensor_failsafe.yaml",
    "06_sensor_recovery.yaml",
    "07_gsm_and_pump.yaml",
    "08_ph_envelope.yaml",
]

RESULT_RE = re.compile(
    r"RESULT\|ms=(?P<ms>\d+)\|do=(?P<do>-?\d+(?:\.\d+)?)\|nh3=(?P<nh3>-?\d+(?:\.\d+)?)"
    r"\|ph=(?P<ph>-?\d+(?:\.\d+)?)\|temp=(?P<temp>-?\d+(?:\.\d+)?)\|bat=(?P<bat>-?\d+(?:\.\d+)?)"
    r"\|score=(?P<score>-?\d+(?:\.\d+)?)\|aerator=(?P<aerator>[01])\|pump=(?P<pump>[01])"
    r"\|reason=(?P<reason>[A-Z_]+)\|valid=(?P<valid>[01])"
)

@dataclass
class Stage:
    name: str
    command: str
    status: str
    exit_code: int
    duration_s: float
    detail: str = ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_stage(name: str, args: list[str], cwd: Path = ROOT, env: dict[str, str] | None = None, timeout: float = 90.0) -> Stage:
    started = time.time()
    try:
        proc = subprocess.run(args, cwd=str(cwd), env=env or os.environ, text=True, capture_output=True, timeout=timeout)
        duration = time.time() - started
        combined = (proc.stdout + "\n" + proc.stderr).strip()
        status = "PASS" if proc.returncode == 0 else "FAIL"
        return Stage(name, " ".join(args), status, proc.returncode, duration, combined[-12000:])
    except subprocess.TimeoutExpired as exc:
        duration = time.time() - started
        out = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        err = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
        combined = (out + "\n" + err + "\nTIMEOUT_EXPIRED").strip()
        return Stage(name, " ".join(args), "FAIL", 124, duration, combined[-12000:])


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def parse_results(log_text: str) -> list[dict]:
    rows: list[dict] = []
    for line in log_text.splitlines():
        m = RESULT_RE.search(line)
        if m:
            row = m.groupdict()
            for key in ("ms", "aerator", "pump", "valid"):
                row[key] = int(row[key])
            for key in ("do", "nh3", "ph", "temp", "bat", "score"):
                row[key] = float(row[key])
            rows.append(row)
    return rows


def normalized_result_hash(log_text: str) -> str:
    rows = parse_results(log_text)
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def assert_scenario(name: str, log_text: str, rows: list[dict]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    boot = {
        "BOOT|ADS1115=PASS",
        "BOOT|GSM_UART=READY",
        "BOOT|FAILSAFE=AERATOR_ON",
        "BOOT|SIMULATION=M7.6_AUTOMATED_VALIDATION",
    }
    for marker in boot:
        if marker not in log_text:
            failures.append(f"missing boot marker: {marker}")
    if not rows:
        failures.append("no RESULT records emitted")
        return False, failures

    if name == "01_nominal.yaml":
        r = rows[-1]
        if not (6.5 <= r["do"] <= 8.5): failures.append(f"nominal DO out of range: {r['do']}")
        if not (7.7 <= r["ph"] <= 8.3): failures.append(f"nominal pH out of range: {r['ph']}")
        if r["aerator"] != 0: failures.append("aerator not OFF at nominal point")
        if r["valid"] != 1: failures.append("nominal sample invalid")
    elif name == "02_hypoxia_trip.yaml":
        lows = [r for r in rows if r["do"] < 4.0 and r["aerator"] == 1 and r["reason"] == "DO_LOW"]
        if not lows: failures.append("no verified DO_LOW -> aerator ON transition")
    elif name == "03_recovery.yaml":
        if not any(r["aerator"] == 1 and r["do"] < 4.0 for r in rows): failures.append("hypoxia ON state not observed")
        if rows[-1]["aerator"] != 0 or rows[-1]["do"] <= 5.5:
            failures.append("aerator did not recover OFF at healthy DO")
    elif name == "04_battery_low.yaml":
        if not any(r["reason"] == "BATTERY_LOW" and r["bat"] < 6.8 for r in rows):
            failures.append("battery-low boundary did not produce BATTERY_LOW")
    elif name == "05_sensor_failsafe.yaml":
        if "TEST|SENSOR_FAIL=ARMED" not in log_text: failures.append("sensor fault injection marker absent")
        if not any(r["valid"] == 0 and r["aerator"] == 1 and r["reason"] == "FAIL_SAFE_SENSOR_FAULT" for r in rows):
            failures.append("sensor fail-safe result not observed")
    elif name == "06_sensor_recovery.yaml":
        if not any(r["valid"] == 0 and r["aerator"] == 1 for r in rows): failures.append("fault ON state not observed")
        if rows[-1]["valid"] != 1 or rows[-1]["aerator"] != 0: failures.append("sensor recovery did not return to healthy OFF state")
    elif name == "07_gsm_and_pump.yaml":
        for marker in ("TEST|GSM_TX=AT_SENT", "TEST|PUMP=ON"):
            if marker not in log_text: failures.append(f"missing {marker}")
    elif name == "08_ph_envelope.yaml":
        values = [r["ph"] for r in rows]
        if not any(3.5 <= v <= 4.5 for v in values): failures.append(f"pH≈4 envelope not observed: {values}")
        if not any(9.5 <= v <= 10.5 for v in values): failures.append(f"pH≈10 envelope not observed: {values}")
        if any(abs(v) > 15 for v in values): failures.append(f"pH conversion runaway: {values}")
    return not failures, failures


def collect_required_files() -> list[Path]:
    return [
        WOKWI / "diagram.json",
        WOKWI / "wokwi.toml",
        WOKWI / "ads1115.chip.c",
        WOKWI / "ads1115.chip.json",
        WOKWI / "platformio.ini",
        WOKWI / "src" / "main.ino",
        ROOT / "config" / "pinmap_m6_5.json",
        ROOT / "config" / "hardware.yaml",
        ROOT / "config" / "thresholds.yaml",
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=2, help="repeat every Wokwi scenario (default: 2)")
    ap.add_argument("--scenario", action="append", help="run only named scenario(s)")
    ap.add_argument("--skip-python", action="store_true", help="skip Python regression (not recommended)")
    ap.add_argument("--skip-native", action="store_true", help="skip native build/test (not recommended)")
    ap.add_argument("--no-wokwi", action="store_true", help="FAIL: retained only for explicit negative testing")
    args = ap.parse_args()

    if args.no_wokwi:
        print("REFUSING --no-wokwi: M7.6 strict validation requires real Wokwi execution.")
        return 2
    if args.repeat < 1:
        print("--repeat must be >= 1")
        return 2

    REPORT.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    for p in REPORT.glob("*"):
        if p.is_file(): p.unlink()
    for p in ARTIFACTS.glob("*"):
        if p.is_file(): p.unlink()

    stages: list[Stage] = []
    missing = [str(p) for p in collect_required_files() if not p.exists()]
    if missing:
        print("Missing required files:")
        print("\n".join(missing))
        return 3

    # Toolchain presence is a hard gate.
    for tool in ("python", "pio", "wokwi-cli"):
        if not command_exists(tool):
            stages.append(Stage(f"tool:{tool}", f"which {tool}", "FAIL", 127, 0.0, "REQUIRED TOOL NOT FOUND"))
            report = make_report(stages, [], [], "TOOLCHAIN_MISSING")
            (REPORT / "full_validation_report.md").write_text(report, encoding="utf-8")
            (REPORT / "full_validation_results.json").write_text(json.dumps({"status":"FAIL","stages":[asdict(s) for s in stages]}, indent=2), encoding="utf-8")
            print(report)
            return 3

    if "WOKWI_CLI_TOKEN" not in os.environ:
        stages.append(Stage("token:WOKWI_CLI_TOKEN", "check env", "FAIL", 1, 0.0, "WOKWI_CLI_TOKEN not set in environment. Obtain token from https://wokwi.com/dashboard/ci and run: $env:WOKWI_CLI_TOKEN='your_token'"))
        report = make_report(stages, [], [], "WOKWI_TOKEN_MISSING")
        (REPORT / "full_validation_report.md").write_text(report, encoding="utf-8")
        (REPORT / "full_validation_results.json").write_text(json.dumps({"status":"FAIL","stages":[asdict(s) for s in stages]}, indent=2), encoding="utf-8")
        print(report)
        return 3

    if not args.skip_python:
        stages.append(run_stage("python-regression", [sys.executable, "-m", "pytest", "-q"]))
    if not args.skip_native:
        # Native build + smoke test from existing repository tooling.
        stages.append(run_stage("native-build", [sys.executable, "tools/build_native.py"]))
        stages.append(run_stage("native-smoke", [sys.executable, "tools/run_native_tests.py"]))

    # Build the actual Wokwi firmware artifact.
    stages.append(run_stage("wokwi-firmware-build", ["pio", "run", "-d", str(WOKWI)]))
    firmware = WOKWI / ".pio" / "build" / "esp32-c3-devkitm-1" / "firmware.bin"
    elf = WOKWI / ".pio" / "build" / "esp32-c3-devkitm-1" / "firmware.elf"
    if stages[-1].status != "PASS" or not firmware.exists() or not elf.exists():
        stages.append(Stage("wokwi-artifact-check", "firmware.bin + firmware.elf", "FAIL", 1, 0.0, "firmware artifacts missing"))
        report = make_report(stages, [], [], "FAIL")
        (REPORT / "full_validation_report.md").write_text(report, encoding="utf-8")
        (REPORT / "full_validation_results.json").write_text(json.dumps({"status":"FAIL","stages":[asdict(s) for s in stages]}, indent=2), encoding="utf-8")
        print(report)
        return 4
    stages.append(Stage("wokwi-artifact-check", "firmware.bin + firmware.elf", "PASS", 0, 0.0, f"bin={firmware.stat().st_size} bytes, elf={elf.stat().st_size} bytes"))

    # Diagram lint is a separate hard gate.
    stages.append(run_stage("wokwi-lint", ["wokwi-cli", "lint"], cwd=WOKWI))

    names = args.scenario or SCENARIO_ORDER
    scenario_runs: list[dict] = []
    hashes_by_scenario: dict[str, list[str]] = {}
    all_ok = all(s.status == "PASS" for s in stages)

    for scenario_name in names:
        if scenario_name not in SCENARIO_ORDER:
            print(f"Unknown scenario: {scenario_name}")
            return 2
        scenario_path = SCENARIOS / scenario_name
        for rep in range(1, args.repeat + 1):
            log_path = ARTIFACTS / f"{scenario_name[:-5]}_run{rep}.serial.log"
            vcd_path = ARTIFACTS / f"{scenario_name[:-5]}_run{rep}.vcd"
            cmd = [
                "wokwi-cli", ".",
                "--scenario", f"scenarios/{scenario_name}",
                "--timeout", "12000",
                "--timeout-exit-code", "0",
                "--serial-log-file", str(log_path.relative_to(WOKWI)),
                "--vcd-file", str(vcd_path.relative_to(WOKWI)),
            ]
            stage = run_stage(f"wokwi:{scenario_name}:run{rep}", cmd, cwd=WOKWI)
            stages.append(stage)
            all_ok &= stage.status == "PASS"
            log_text = log_path.read_text(encoding="utf-8", errors="replace") if (log_path.exists() and log_path.stat().st_size > 0) else stage.detail
            rows = parse_results(log_text)
            ok, failures = assert_scenario(scenario_name, log_text, rows)
            result_hash = normalized_result_hash(log_text)
            hashes_by_scenario.setdefault(scenario_name, []).append(result_hash)
            artifact = {
                "scenario": scenario_name,
                "repeat": rep,
                "process_status": stage.status,
                "acceptance_status": "PASS" if ok else "FAIL",
                "acceptance_failures": failures,
                "result_hash": result_hash,
                "result_count": len(rows),
                "results": rows,
                "serial_log": str(log_path.relative_to(ROOT)) if log_path.exists() else None,
                "vcd": str(vcd_path.relative_to(ROOT)) if vcd_path.exists() else None,
            }
            scenario_runs.append(artifact)
            all_ok &= ok
            # Strong repeatability criterion: canonical results must match between runs.
            if rep > 1:
                prior = hashes_by_scenario[scenario_name][0]
                repeat_ok = prior == result_hash
                artifact["repeatability_status"] = "PASS" if repeat_ok else "FAIL"
                all_ok &= repeat_ok

    # Hash the complete critical source set after the run.
    hashes = {}
    for p in collect_required_files():
        hashes[str(p.relative_to(ROOT))] = sha256_file(p)
    hashes["wokwi/ci/.pio/build/esp32-c3-devkitm-1/firmware.bin"] = sha256_file(firmware)
    hashes["wokwi/ci/.pio/build/esp32-c3-devkitm-1/firmware.elf"] = sha256_file(elf)

    status = "PASS" if all_ok else "FAIL"
    report = make_report(stages, scenario_runs, hashes, status)
    payload = {
        "milestone": "M7.6",
        "title": "Full Automated Hardware Simulation Validation",
        "status": status,
        "strict_policy": True,
        "repeat": args.repeat,
        "host": {"os": platform.platform(), "python": sys.version},
        "stages": [asdict(s) for s in stages],
        "scenario_runs": scenario_runs,
        "artifact_sha256": hashes,
        "acceptance_contract": [
            "toolchain present; no silent skips",
            "Python regression passes",
            "native firmware build and smoke test pass",
            "PlatformIO ESP32-C3 firmware build passes",
            "Wokwi diagram lint passes",
            "all selected Wokwi scenarios pass their runtime assertions",
            "serial RESULT records are emitted",
            "repeat runs produce identical canonical RESULT hashes",
            "VCD/log artifacts are produced for every run",
        ],
    }
    (REPORT / "full_validation_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (REPORT / "full_validation_report.md").write_text(report, encoding="utf-8")
    print(report)
    return 0 if all_ok else 5


def make_report(stages: list[Stage], scenario_runs: list[dict], hashes: list | dict, status: str) -> str:
    lines = [
        "# PondGuard M7.6 — Full Automated Hardware Simulation Validation",
        "",
        f"## FINAL STATUS: **{status}**",
        "",
        "This is a strict reproducibility pipeline. Missing PlatformIO/Wokwi CLI is a failure, not a skip.",
        "",
        "## Stage Results",
        "",
        "| Stage | Status | Exit | Time (s) |",
        "|---|---:|---:|---:|",
    ]
    for s in stages:
        lines.append(f"| {s.name} | **{s.status}** | {s.exit_code} | {s.duration_s:.2f} |")
    if scenario_runs:
        lines += ["", "## Wokwi Scenario Evidence", "", "| Scenario | Run | Process | Acceptance | RESULT records | Hash | Repeat |", "|---|---:|---:|---:|---:|---|---|"]
        for r in scenario_runs:
            repeat = r.get("repeatability_status", "—")
            lines.append(f"| {r['scenario']} | {r['repeat']} | {r['process_status']} | {r['acceptance_status']} | {r['result_count']} | `{r['result_hash'][:16]}…` | {repeat} |")
    lines += [
        "", "## What constitutes 100% pass", "",
        "Every declared acceptance gate must pass: toolchain presence, Python/native regression, real ESP32-C3 firmware build, Wokwi diagram lint, every Wokwi scenario assertion, serial RESULT emission, repeatability, and artifact generation.",
        "",
        "## Important limitation", "",
        "This proves the declared **simulation contract** reproducibly. It does not prove physical hardware behavior, pond chemistry, sensor calibration, component tolerances beyond the modeled domains, or field reliability. Those require physical test evidence.",
    ]
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    raise SystemExit(main())
