# PondGuard — Autonomous Aquaculture Control & Hardware Simulation System

[![Python Regression](https://img.shields.io/badge/Python%20Tests-93%2F93%20Passed-brightgreen)](tests/)
[![PlatformIO Build](https://img.shields.io/badge/PlatformIO-ESP32--C3%20DevKitM--1-blue)](wokwi/ci/platformio.ini)
[![Hardware Freeze](https://img.shields.io/badge/Hardware%20Status-M7.5%20Design%20Freeze%20Candidate-orange)](reports/m7_5/design_freeze_manifest.json)
[![Simulation Pipeline](https://img.shields.io/badge/Pipeline-M7.6%20Strict%20Evidence-success)](tools/run_full_validation.py)

**PondGuard** is a code-first, rigorous embedded environmental monitoring and autonomous aeration control system designed for high-density aquaculture ponds (e.g., *Litopenaeus vannamei* shrimp and finfish farming). 

The platform integrates multi-parameter water quality acquisition (Dissolved Oxygen, pH, Ammonia gas proxy, Temperature), multi-rail solar power management, non-volatile datalogging, cellular telemetry, and a fail-safe dual-actuator control loop running on an Espressif ESP32-C3 microcontroller.

---

## Table of Contents

1. [System Overview & Engineering Mission](#1-system-overview--engineering-mission)
2. [Authoritative Single Sources of Truth](#2-authoritative-single-sources-of-truth)
3. [Core Invariants & Safety Mandates](#3-core-invariants--safety-mandates)
4. [Hardware Subsystem Architecture](#4-hardware-subsystem-architecture)
   - [4.1 MCU & Strapping Pin Strategy](#41-mcu--strapping-pin-strategy)
   - [4.2 Power Subsystem & Multi-Rail Regulation](#42-power-subsystem--multi-rail-regulation)
   - [4.3 Dissolved Oxygen (DO) Analog Front-End](#43-dissolved-oxygen-do-analog-front-end)
   - [4.4 pH Differential Analog Front-End](#44-ph-differential-analog-front-end)
   - [4.5 Qualitative Ammonia ($NH_3$) Sensor Interface](#45-qualitative-ammonia-nh_3-sensor-interface)
   - [4.6 Temperature & Digital Peripherals](#46-temperature--digital-peripherals)
5. [Pin Allocation & Bus Map](#5-pin-allocation--bus-map)
6. [Firmware & Controller Control Logic](#6-firmware--controller-control-logic)
   - [6.1 Multi-Factor Crash Risk Scoring](#61-multi-factor-crash-risk-scoring)
   - [6.2 State Machine & Actuator Hysteresis](#62-state-machine--actuator-hysteresis)
7. [Electrical & SPICE Validation Stack (M7.1 – M7.5)](#7-electrical--spice-validation-stack-m71--m75)
   - [7.1 SPICE Equivalent Reference Models (M7.2)](#71-spice-equivalent-reference-models-m72)
   - [7.2 Parametric Tolerance & Monte Carlo Sweeps (M7.3)](#72-parametric-tolerance--monte-carlo-sweeps-m73)
   - [7.3 Worst-Case GSM Transient & Battery Sag Analysis (M7.4)](#73-worst-case-gsm-transient--battery-sag-analysis-m74)
   - [7.4 Hardware Simulation Design-Freeze Manifest (M7.5)](#74-hardware-simulation-design-freeze-manifest-m75)
8. [Automated Hardware Validation Pipeline (M7.6)](#8-automated-hardware-validation-pipeline-m76)
   - [8.1 Test Scenario Matrix](#81-test-scenario-matrix)
   - [8.2 Evidence & Repeatability Proof](#82-evidence--repeatability-proof)
9. [Project Directory & Artifact Structure](#9-project-directory--artifact-structure)
10. [Verification & Quickstart Guide](#10-verification--quickstart-guide)
11. [Scientific Integrity & Claim Boundaries](#11-scientific-integrity--claim-boundaries)

---

## 1. System Overview & Engineering Mission

Hypoxia (dissolved oxygen < 4.0 mg/L) and toxic un-ionized ammonia spikes are the primary causes of catastrophic biomass mortality in commercial aquaculture. PondGuard provides:
- **Continuous multi-parameter environmental sensing**: Galvanic DO, glass-electrode pH, 1-Wire water temperature, qualitative NH3 headspace gas, and battery rail telemetry.
- **Fail-safe aeration control**: The aerator relay is designed as a physical fail-safe actuator (normally energized / active ON upon system fault, sensor invalidity, or hypoxia).
- **Zero silent failures**: Any out-of-range sensor voltage, bus timeout, or power brownout forces a fail-safe state and triggers an immediate diagnostic reason.
- **Mathematical determinism**: All control thresholds, filter poles, resistor dividers, and energy balances are verified using parametric Python sweeps, SPICE netlists, and CI automation.

---

## 2. Authoritative Single Sources of Truth

In accordance with repository guidelines, hardware pin allocations, threshold definitions, and mathematical constants are **never silently duplicated** in application code. All firmware, simulation harnesses, tests, and documentation strictly derive from these authoritative configuration files:

| Configuration File | Scope & Authority |
| :--- | :--- |
| `config/hardware.yaml` | Pin assignments, supply voltages, component ratings, passive values, ADC channel allocations |
| `config/thresholds.yaml` | Biological thresholds (DO ON/OFF, pH ranges, NH3 alarms), sensor valid voltage windows |
| `config/simulation.yaml` | Virtual pond physics constants, diurnal reaeration/respiration rates, noise parameters |
| `config/pinmap_m6_5.json` | Validated collision-free pin mapping schema for ESP32-C3 |
| `hardware/bom/M6_7_BOM.csv` | Pre-fabrication Bill of Materials freeze candidate with exact active MPNs |

---

## 3. Core Invariants & Safety Mandates

1. **Aerator Fail-Safe ON**: The aerator SSR relay output on `GPIO 0` must default to **ON (HIGH)** upon boot, watchdog trip, sensor failure, or communication loss.
2. **DO Pump Fail-Safe OFF**: The DO circulation sampling pump on `GPIO 1` must default to **OFF (LOW)** on boot or fault to prevent dry-running or battery exhaustion.
3. **Strapping Pin Isolation**: ESP32-C3 strapping pins (`GPIO 2`, `GPIO 8`, `GPIO 9`) and internal flash pins (`GPIO 12-17`) are **strictly avoided** and left unconnected on the PCB.
4. **JTAG & SPI Mutual Exclusivity**: `GPIO 18` and `GPIO 19` are dedicated to the MicroSD SPI bus (`MOSI` and `MISO`), deliberately disabling USB-JTAG during runtime.
5. **No Direct Mains Connection**: Relay outputs represent low-voltage logical control signals to external optical-isolated SSR / contactor stages; never connect MCU GPIO directly to mains loads.
6. **No Fabricated Calibration**: SEN0567 MEMS is strictly qualitative gas concentration in chamber air. No dissolved NH3 (mg/L) calibration is claimed without empirical titration chamber validation.

---

## 4. Hardware Subsystem Architecture

```
                                  +-----------------------+
                                  |   18V Solar Panel     |
                                  +-----------+-----------+
                                              |
                                              v
+------------------+              +-----------------------+
|  2S Li-ion Pack  |<============>|  CN3722 MPPT Charger  |
|  (6.0V - 8.4V)   |  BMS >= 5A   +-----------+-----------+
+--------+---------+                          |
         |                                    | VBAT Rail
         +--------------------+---------------+
                              |
       +----------------------+----------------------+
       |                      |                      |
       v                      v                      v
+--------------+      +---------------+      +---------------+
|  TI LMR51430 |      |  TI LMR51430  |      |  TI LMR51430  |
|   Buck 5V    |      |   Buck 3.3V   |      |  Buck 4.0V GSM|
+-------+------+      +-------+-------+      +-------+-------+
        |                     |                      |
        | 5V_SYS              | 3V3                  | 4V_GSM (4,700uF Bulk)
        |                     |                      |
        +-- Relays            +-- ESP32-C3           +-- SIM800L Cellular
        +-- DO TIA (Opt B)    +-- ADS1115 ADC
                              +-- AD8607 pH Buffer
                              +-- DS18B20 Temp
                              +-- MicroSD SPI
```

### 4.1 MCU & Strapping Pin Strategy
- **Microcontroller**: Espressif ESP32-C3 RISC-V 32-bit single-core @ 160 MHz.
- **Strapping Protection**: `GPIO 2` (bootstrap), `GPIO 8` (flash voltage/boot), and `GPIO 9` (boot mode) are completely isolated from peripheral loading to eliminate boot hangs.
- **Hardware Serial**: Default console UART0 on `GPIO 20` (`RX`) and `GPIO 21` (`TX`).

### 4.2 Power Subsystem & Multi-Rail Regulation
- **Solar Charging**: **CN3722** MPPT step-down charger (7.5V-28V input range, configured for 2S Li-ion float voltage of 8.40V and 18V Vmp tracking).
- **Battery Pack**: 2S Li-ion (7.4V nominal, 6.0V cutoff, 8.4V max) with >= 5A continuous BMS protection.
- **System Buck Regulators**: High-efficiency **Texas Instruments LMR51430XFDDCR** (36V input, 3A continuous, 1.1 MHz switching) for:
  - **`5V_SYS`**: R_top = 732 kOhm, R_bot = 100 kOhm -> 4.992 V (Relay coils, DO sensor).
  - **`3V3`**: R_top = 453 kOhm, R_bot = 100 kOhm -> 3.318 V (MCU, ADS1115, AD8607, SD card).
  - **`SIM800_4V`**: R_top = 562 kOhm, R_bot = 100 kOhm -> 3.972 V with dedicated 4,700 uF low-ESR bulk capacitance for 2A / 1ms 2G bursts.

### 4.3 Dissolved Oxygen (DO) Analog Front-End
- **Sensor**: Galvanic membrane DO probe (DFRobot SEN0237-A or raw galvanic cell generating 0-35 uA).
- **Branch A (Industrial Module)**: SEN0237-A signal-conditioner producing 0-3.0 V for 0-12 mg/L DO.
- **Branch B (Custom Precision TIA)**: Low-noise transimpedance amplifier (Rf = 47 kOhm, Cf = 100 nF) yielding fc = 1 / (2*pi*Rf*Cf) = 33.86 Hz for high 50/60 Hz line-noise rejection.
- **Acquisition**: **ADS1115 AIN1** (Single-ended, PGA GAIN_ONE +-4.096 V, 16-bit resolution ~125 uV/LSB).

### 4.4 pH Differential Analog Front-End
- **Electrode**: High-impedance (10^7 - 10^9 Ohm) glass pH probe generating Nernst potential (E0 +- 59.16 mV/pH at 25 deg C).
- **AFE Topology**: Analog Devices **AD8607** dual ultra-low input bias current (IB < 1 pA) precision op-amp.
  - Channel A: High-impedance unity-gain voltage follower for the pH glass electrode.
  - Channel B: Low-impedance 1.650V pseudo-ground reference generator (3.3V divider buffered).
- **Acquisition**: **ADS1115 Differential Mode** between **AIN0** (pH Signal) and **AIN3** (1.65V Bias).
- **Dynamic Range**: Over pH 4.0-10.0 and temperature 0-50 deg C, differential voltage spans -192.4 mV to +192.4 mV, matching ADS1115 PGA ranges without clipping.

### 4.5 Qualitative Ammonia (NH3) Sensor Interface
- **Sensor**: DFRobot Fermion SEN0567 MEMS metal-oxide gas sensor (1-500 ppm chamber range).
- **Protection Network**: First-order low-pass filter (R = 1.0 kOhm, C = 100 nF -> fc = 1.591 kHz) with dual Schottky clamping to 3.3V and GND.
- **Acquisition**: **ESP32-C3 GPIO 5** ADC input.
- **Interpretation Rule**: Documented explicitly as a **qualitative headspace proxy**; cannot be converted to dissolved NH3 (mg/L) without empirical pH/temperature chamber calibration.

### 4.6 Temperature & Digital Peripherals
- **Water Temperature**: Maxim **DS18B20** 1-Wire sensor on `GPIO 4` with 4.7 kOhm pullup (-55 deg C to +125 deg C, +-0.5 deg C accuracy).
- **Datalogger**: MicroSD card breakout on SPI bus (`SCK`: `GPIO 10`, `MOSI`: `GPIO 18`, `MISO`: `GPIO 19`, `CS`: `GPIO 3`).
- **Cellular Telemetry**: SIMCom SIM800L 2G quad-band modem on UART (`TX`: `GPIO 21`, `RX`: `GPIO 20`).
- **Actuators**: Optically isolated solid-state relays (SSR) on `GPIO 0` (Aerator) and `GPIO 1` (Circulation Pump).

---

## 5. Pin Allocation & Bus Map

All pins have been verified conflict-free per `config/pinmap_m6_5.json`:

```
                       ESP32-C3 DevKitM-1 Pinout
                            +---------------+
                     3V3.1 -| 1          18 |- GND.1
                     GPIO0 -| 2          17 |- TX (GPIO21)  <-- GSM TX / Console
                     GPIO1 -| 3          16 |- RX (GPIO20)  <-- GSM RX / Console
                     GPIO2 -| 4 [STRAP]  15 |- GPIO19       <-- MicroSD MISO
                     GPIO3 -| 5          14 |- GPIO18       <-- MicroSD MOSI
                     GPIO4 -| 6          13 |- GPIO10       <-- MicroSD SCK
                     GPIO5 -| 7          12 |- GPIO9  [STRAP]
                     GPIO6 -| 8          11 |- GPIO8  [STRAP]
                     GPIO7 -| 9          10 |- 5V.1
                            +---------------+
```

| MCU Pin | Peripheral / Function | Logic Level | Direction | Invariant / Circuit Protection |
| :--- | :--- | :--- | :--- | :--- |
| **`GPIO 0`** | Aerator SSR Relay | 3.3V CMOS | Output | **Fail-safe ON** (`HIGH` active) |
| **`GPIO 1`** | DO Pump SSR Relay | 3.3V CMOS | Output | **Fail-safe OFF** (`LOW` safe) |
| **`GPIO 2`** | *Unused (Strapping)* | — | — | Strapping pin isolated; left floating/pull |
| **`GPIO 3`** | MicroSD SPI Chip Select (`CS`) | 3.3V CMOS | Output | Active `LOW` chip select |
| **`GPIO 4`** | DS18B20 1-Wire Data (`DQ`) | 3.3V Open-Drain | Bidirectional | 4.7 kOhm pullup to 3.3V |
| **`GPIO 5`** | SEN0567 NH3 Analog ADC | 0-3.3V | Input (ADC1_CH5) | 1.0 kOhm + 100 nF RC (1.59 kHz) |
| **`GPIO 6`** | I2C Bus SDA (ADS1115) | 3.3V Open-Drain | Bidirectional | 4.7 kOhm pullup; 400 kHz |
| **`GPIO 7`** | I2C Bus SCL (ADS1115) | 3.3V Open-Drain | Output | 4.7 kOhm pullup; 400 kHz |
| **`GPIO 8`** | *Unused (Strapping)* | — | — | Strapping pin isolated |
| **`GPIO 9`** | *Unused (Strapping)* | — | — | Strapping pin / Boot button isolated |
| **`GPIO 10`** | MicroSD SPI Clock (`SCK`) | 3.3V CMOS | Output | SPI Clock up to 20 MHz |
| **`GPIO 18`** | MicroSD SPI Data In (`MOSI`)| 3.3V CMOS | Output | SPI Master Out Slave In |
| **`GPIO 19`** | MicroSD SPI Data Out (`MISO`)| 3.3V CMOS | Input | SPI Master In Slave Out |
| **`GPIO 20`** | Hardware UART RX (GSM / Serial)| 3.3V CMOS | Input | SIM800L TX -> ESP32 RX |
| **`GPIO 21`** | Hardware UART TX (GSM / Serial)| 3.3V CMOS | Output | ESP32 TX -> SIM800L RX (1k/10k div) |

### ADS1115 16-Bit I2C ADC Allocation (`0x48`)
- **`AIN0`**: pH Buffered Probe Signal (0.8-2.5 V)
- **`AIN1`**: Dissolved Oxygen Conditioned Voltage (0-3.0 V = 0-12.0 mg/L)
- **`AIN2`**: Battery Voltage Monitor (10 kOhm / 3.3 kOhm divider; 8.4V -> 2.084V)
- **`AIN3`**: pH 1.650V Pseudo-Ground Bias (Differential reference)

---

## 6. Firmware & Controller Control Logic

The firmware in `firmware/src/control/controller.cpp` implements a portable, platform-independent, test-driven state machine in ISO C++17.

```
                           +------------------------+
                           |     SENSOR ACQUISITION |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
              +----------->|   VALID TELEMETRY?     |------------+
              |            +-----------+------------+            |
              |                        | YES                     | NO (Fault)
              |                        v                         v
              |            +------------------------+  +-------------------+
              |            | COMPUTE CRASH RISK     |  | FAIL-SAFE OVERRIDE|
              |            | SCORE (0 - 100)        |  | Aerator: ON       |
              |            +-----------+------------+  | Reason: FAULT     |
              |                        |               +-------------------+
              |                        v
              |            +------------------------+
              |            |  DO < 4.0 mg/L?        |----> [Aerator ON (DO_LOW)]
              |            +-----------+------------+
              |                        | NO
              |                        v
              |            +------------------------+
              |            |  Score >= 70?          |----> [Aerator ON (CRASH_HIGH)]
              |            +-----------+------------+
              |                        | NO
              |                        v
              |            +------------------------+
              |            |  DO > 5.5 & Score < 45?|----> [Aerator OFF (NORMAL)]
              |            +-----------+------------+
              |                        | NO
              |                        v
              |            +------------------------+
              +------------|    HYSTERESIS HOLD     |
                           +------------------------+
```

### 6.1 Multi-Factor Crash Risk Scoring
The crash score S in [0, 100] evaluates impending hypoxia risks by combining normalized linear risk terms:

```
S = 100 * ( 0.38 * R_DO + 0.22 * R_trend + 0.25 * R_NH3 + 0.05 * R_temp + 0.10 * R_time )
```

Where:
- R_DO = clamp01((5.5 - DO) / 2.0): Proximity to the 4.0 mg/L hypoxia trip line.
- R_trend = clamp01((-dDO/dt) / 0.30 mg/L/min): Rate of DO depletion.
- R_NH3 = clamp01(NH3 / 0.50): Ammonia gas accumulation.
- R_temp = clamp01((T - 30.0 deg C) / 5.0 deg C): Thermal oxygen solubility depression.
- R_time = 1.0 at night (18:00-06:00, respiration dominance) and 0.25 during daytime (photosynthesis).

### 6.2 State Machine & Actuator Hysteresis
- **Emergency Aeration Trip**: If DO < 4.0 mg/L -> Aerator ON (`DO_LOW`).
- **High Combined Risk Trip**: If S >= 70.0 -> Aerator ON (`CRASH_SCORE_HIGH`).
- **Recovery Threshold**: If DO > 5.5 mg/L AND S < 45.0 -> Aerator OFF (`NORMAL`).
- **Deadband / Hysteresis**: In the intermediate window (4.0 <= DO <= 5.5 mg/L), the previous actuator state is latched (`HYSTERESIS_HOLD`).
- **Battery Warning**: If V_bat < 6.80 V -> Reason `BATTERY_LOW` (logged to SD/GSM; aerator continues running to protect aquatic life until BMS cutoff).

---

## 7. Electrical & SPICE Validation Stack (M7.1 – M7.5)

### 7.1 SPICE Equivalent Reference Models (M7.2)
Deterministic mathematical models and SPICE netlists in `simulation/m7_2/`:
- **DO Transimpedance Amplifier**: Rf = 47 kOhm +-1%, Cf = 100 nF +-10% -> fc = 33.86 Hz.
- **pH Nernst Transfer**: V_diff = (7.0 - pH) * 59.16 mV/pH at 25 deg C.
- **Ammonia Low-Pass Filter**: R = 1.0 kOhm, C = 100 nF -> fc = 1.591 kHz.
- **2S Battery Divider**: R1 = 10 kOhm, R2 = 3.3 kOhm -> Ratio = 4.0303 -> 8.40V -> 2.084V.

### 7.2 Parametric Tolerance & Monte Carlo Sweeps (M7.3)
5,000-sample Monte Carlo distributions across passive tolerances (+-1% resistors, +-10% capacitors, +-5% sensor variations):
- **DO TIA Cutoff Frequency**: 30.72 Hz to 37.47 Hz (100% within 20-60 Hz design envelope).
- **pH Differential Span**: +-192.39 mV maximum over 0-50 deg C (100% within ADS1115 +-512 mV range).
- **Battery Voltage ADC Node**: Maximum 2.111 V <= 3.00 V absolute ADC safety limit.

### 7.3 Worst-Case GSM Transient & Battery Sag Analysis (M7.4)
Dynamic model of the 4.0V GSM rail under 2.0A / 1ms 2G transmit pulses:
- **Regulator Response Delay**: Swept tau_reg in [10 us, 100 us].
- **Capacitor Sizing Result**: 2,200 uF is mathematically insufficient (voltage drops to 3.09V < 3.4V cutoff). Minimum robust modeled bulk capacitance is **3,300 uF**; **4,700 uF** frozen as the candidate for design margin.
- **Battery Terminal Sag**: Under worst-case simultaneous peak load (15.64W), internal pack resistance (Rs ~ 100 mOhm) sags a 6.0V pack to 5.85V. Low-battery trip policy frozen at **6.4-6.8V OCV**.

### 7.4 Hardware Simulation Design-Freeze Manifest (M7.5)
The simulation stack is frozen under SHA-256 integrity verification in `reports/m7_5/design_freeze_manifest.json`.

---

## 8. Automated Hardware Validation Pipeline (M7.6)

PondGuard features a strict, automated end-to-end evidence pipeline executed via a single command:

```bash
python tools/run_full_validation.py
```

### 8.1 Test Scenario Matrix

| Scenario File | Target Condition | Injected Stimulus | Mandatory Assertion Gate |
| :--- | :--- | :--- | :--- |
| `01_nominal.yaml` | Nominal water quality | DO = 7.2 mg/L, pH = 8.0 | `GPIO 0` **OFF** (`0`), valid telemetry |
| `02_hypoxia_trip.yaml` | Hypoxia protection | DO knob dragged to 2.4 mg/L | `GPIO 0` **ON** (`1`), `reason=DO_LOW` |
| `03_recovery.yaml` | Hysteresis recovery | DO -> 2.4 -> 8.4 mg/L | `GPIO 0` **ON** -> `GPIO 0` **OFF** (`0`) |
| `04_battery_low.yaml` | Battery boundary | V_bat = 6.65 V < 6.8 V | `reason=BATTERY_LOW` emitted |
| `05_sensor_failsafe.yaml` | Sensor fault injection | `TEST SENSOR_FAIL` | `GPIO 0` **ON** (`1`), `reason=FAIL_SAFE` |
| `06_sensor_recovery.yaml` | Sensor fault recovery | `TEST SENSOR_FAIL` -> `OK` | `GPIO 0` **ON** -> `GPIO 0` **OFF** (`0`) |
| `07_gsm_and_pump.yaml` | Peripherals | `TEST GSM`, `TEST PUMP` | `TEST|GSM_TX=AT_SENT`, `GPIO 1` pulse |
| `08_ph_envelope.yaml` | Differential pH span | Differential pots -> pH 4, 10 | pH ~ 4.0 and pH ~ 10.0 recorded |

### 8.2 Evidence & Repeatability Proof
Every scenario is executed **twice** by default. Canonical structured `RESULT|...` telemetry records are extracted and SHA-256 hashed across both runs:
- Hash_Run1 == Hash_Run2 -> **REPEATABILITY = PASS**.
- Outputs saved to `reports/m7_6/` with raw logic analyzer waveform captures in `wokwi/ci/artifacts/*.vcd`.

---

## 9. Project Directory & Artifact Structure

```
PondGuard_Wokwi_Full_Hardware_Simulation/
├── config/                         # Authoritative sources of truth
│   ├── hardware.yaml               # Pin maps, rails, passive values
│   ├── thresholds.yaml             # Biological control thresholds
│   ├── simulation.yaml             # Virtual pond model parameters
│   └── pinmap_m6_5.json            # ESP32-C3 collision-free map
├── docs/                           # Technical documentation & design decisions
│   ├── architecture.md             # System architecture manual
│   ├── M7_6_PANEL_DEMO.md          # Live panel review demonstration script
│   └── decisions/                  # Architecture Decision Records (ADRs 0001-0009)
├── firmware/                       # Production C++17 controller
│   ├── include/ponguard/           # Controller headers & SI data structures
│   └── src/control/controller.cpp  # Portable control logic implementation
├── hardware/                       # Electrical schematics, SPICE, BOMs
│   ├── bom/M6_7_BOM.csv            # Pre-fabrication BOM freeze candidate
│   ├── kicad/                      # PondGuard unified KiCad schematics
│   ├── do_afe/                     # Galvanic DO TIA circuit & SPICE
│   ├── ph_afe/                     # AD8607 differential pH circuit & SPICE
│   ├── nh3_interface/              # SEN0567 RC filter & protection circuit
│   └── power/                      # Multi-rail buck regulators & power audit
├── simulation/                     # Electrical & Monte Carlo simulation engines
│   ├── m7_2/                       # SPICE reference simulation scripts
│   ├── m7_3/                       # 5,000-sample parametric tolerance sweeps
│   ├── m7_4/                       # Worst-case GSM transient & battery sag models
│   └── m7_5/finalize.py            # SHA-256 design freeze generator
├── tests/                          # 93 automated pytest unit & regression tests
├── tools/                          # Command-line validation & build utilities
│   ├── build_native.py             # Compiles native C++ controller with g++
│   ├── run_native_tests.py         # Executes native C++ test suite
│   ├── run_full_validation.py      # M7.6 master validation pipeline runner
│   ├── validate_config.py          # Configuration consistency validator
│   ├── validate_pinmap.py          # Collision-free pin map validator
│   └── validate_m6_7.py            # Pre-fabrication BOM validator
├── wokwi/                          # Wokwi simulation workspace
│   ├── ci/                         # CI automation harness, PlatformIO & scenarios
│   │   ├── diagram.json            # ESP32-C3 Wokwi circuit schematic
│   │   ├── wokwi.toml              # Wokwi simulator configuration
│   │   ├── platformio.ini          # PlatformIO ESP32-C3 build configuration
│   │   ├── ads1115.chip.c          # ADS1115 custom C chip source
│   │   ├── ads1115.chip.wasm       # Compiled WebAssembly chip binary
│   │   ├── scenarios/              # 8 YAML automation scenarios
│   │   └── src/main.ino            # Wokwi firmware sketch
│   └── diagram.json                # Root visual Wokwi workspace
└── README.md                       # Definitive master documentation
```

---

## 10. Verification & Quickstart Guide

### Prerequisites
- **Python 3.10+** (`pip install -r requirements-dev.txt`)
- **GCC / MinGW C++17 Compiler** (`g++` on PATH)
- **PlatformIO Core** (`pip install platformio`)
- **Wokwi CLI** (`iwr https://wokwi.com/ci/install.ps1 -useb | iex`)
- **VS Code Wokwi Extension** (for interactive visual simulation)

### One-Command Full Validation
```bash
python tools/run_full_validation.py
```

### Individual Subsystem Checks
```powershell
# 1. Run complete Python regression suite (93 tests)
python -m pytest

# 2. Build and verify native C++ controller
python tools/build_native.py
python tools/run_native_tests.py

# 3. Compile ESP32-C3 firmware
pio run -d wokwi/ci

# 4. Lint Wokwi circuit diagram
cd wokwi/ci; wokwi-cli lint; cd ../..

# 5. Run single-source configuration and pin validators
python tools/validate_config.py
python tools/validate_pinmap.py
python tools/validate_m6_7.py
python hardware/power/power_review.py

# 6. Re-generate M7.5 Design Freeze SHA-256 Manifest
python simulation/m7_5/finalize.py
```

### Interactive Live Simulation in VS Code
1. Open `wokwi/ci/diagram.json` in VS Code.
2. Press `F1` -> **Wokwi: Start Simulator**.
3. Adjust the **DO**, **pH**, **Battery**, or **NH3** potentiometers to observe live aerator switching, relay activation, and serial telemetry.
4. Refer to `docs/M7_6_PANEL_DEMO.md` for the live demonstration script.

---

## 11. Scientific Integrity & Claim Boundaries

To ensure scientific and engineering integrity:
1. **Simulation vs. Physical Hardware**: This repository proves the **declared simulation contract** reproducibly across mathematical and electrical models. It does not replace physical PCB fabrication testing, wet-bench bring-up, or pond-side field trials.
2. **Sensor Calibration**: SEN0567 is treated strictly as a **qualitative gas indicator**. No claim of direct dissolved NH3 (mg/L) accuracy is made without empirical chamber calibration.
3. **Pre-Fabrication Status**: The hardware BOM and KiCad schematics are frozen at **Candidate Status (M6.7/M7.5)**. Physical fabrication requires final KiCad GUI ERC/DRC verification and footprint assignment.
4. **Energy Balance**: Solar harvesting calculations assume standard test conditions (1000 W/m^2, 25 deg C); actual cloudy-day autonomy depends on local geographic irradiance.
