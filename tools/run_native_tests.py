from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
build = ROOT / "build_m4"
build.mkdir(exist_ok=True)

cmd = [
    "g++", "-std=c++17", "-O2",
    "-I", str(ROOT / "firmware/include"),
    str(ROOT / "firmware/src/control/controller.cpp"),
    str(ROOT / "firmware/test/test_controller_native.cpp"),
    "-o", str(build / "test_controller_native"),
]

r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
print(r.stdout)
print(r.stderr)
if r.returncode != 0:
    print(r.stderr)
    raise SystemExit(r.returncode)
print("BUILD PASS")

r = subprocess.run([str(build / "test_controller_native")], cwd=ROOT, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr)
    raise SystemExit(r.returncode)
print("SMOKE TEST PASS")
raise SystemExit(0)
