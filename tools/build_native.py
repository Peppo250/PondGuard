from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
build = ROOT / "build_m4"
build.mkdir(exist_ok=True)

sources = [
    ROOT / "firmware/src/control/controller.cpp",
    ROOT / "firmware/src/native_main.cpp",
]

cmd = [
    "g++", "-std=c++17", "-O2",
    "-I", str(ROOT / "firmware/include"),
    *map(str, sources),
    "-o", str(build / "pondguard_native"),
]

print("Building:", " ".join(cmd))
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
raise SystemExit(result.returncode)
