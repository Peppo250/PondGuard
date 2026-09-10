from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'hardware' / 'kicad' / 'PondGuard_M6_6_Unified.sch'
OUT.parent.mkdir(parents=True, exist_ok=True)

comps = []

def comp(lib, ref, value, x, y, orient='1 0 0 -1', footprint='', fields=None):
    uid = f'{len(comps)+1:08X}'
    comps.append((lib, ref, value, x, y, orient, footprint, fields or {}))

# Core symbols / modules represented as connectors or generic symbols.
comp('Connector_Generic:Conn_01x16', 'J_MCU', 'ESP32-C3', 5650, 3850, footprint='Module:ESP32-C3-MINI-1')
comp('Connector_Generic:Conn_01x10', 'J_ADC', 'ADS1115', 3600, 2650, footprint='Package_DIP:DIP-10_W7.62mm')
comp('Connector_Generic:Conn_01x03', 'J_PH', 'pH electrode', 1100, 2050, footprint='Connector_Coaxial:BNC')
comp('Connector_Generic:Conn_01x02', 'J_DO', 'DO interface', 1100, 3050)
comp('Connector_Generic:Conn_01x03', 'J_NH3', 'SEN0567', 1100, 4050)
comp('Connector_Generic:Conn_01x03', 'J_TEMP', 'DS18B20', 1100, 4900)
comp('Connector_Generic:Conn_01x04', 'J_SD', 'MicroSD', 8300, 2500)
comp('Connector_Generic:Conn_01x04', 'J_GSM', 'SIM800L', 8300, 4050)
comp('Connector_Generic:Conn_01x03', 'J_AER', 'Aerator driver input', 8300, 5200)
comp('Connector_Generic:Conn_01x03', 'J_PUMP', 'DO pump driver input', 8300, 5900)
comp('Connector_Generic:Conn_01x04', 'J_PWR', 'System power', 1800, 6500)
comp('Connector_Generic:Conn_01x04', 'J_SENSE_PWR', 'Rails', 3600, 6500)

# Power components
comp('Device:Fuse', 'F1', '1A', 2450, 6350)
comp('Device:D', 'D1', 'TVS 5.1V', 2850, 6350)
comp('Device:R', 'R_BATT_TOP', '10k', 2900, 5850)
comp('Device:R', 'R_BATT_BOT', '3.3k', 2900, 6200)
comp('Device:C', 'C_GSM_BULK', '100uF LOW-ESR', 6900, 4050)
comp('Device:C', 'C_GSM_LOCAL', '4.7uF', 7300, 4050)
comp('Device:C', 'C_NH3', '100nF', 1850, 4050)
comp('Device:R', 'R_NH3', '1k', 1550, 4050)
comp('Device:R', 'R_DS_PULL', '4.7k', 1550, 4900)
comp('Device:R', 'R_GSM_SER', '1k', 6900, 3650)
comp('Device:R', 'R_GSM_PD', '10k', 7300, 3650)
comp('Device:R', 'R_PH_TOP', '10k', 1850, 1700)
comp('Device:R', 'R_PH_BOT', '10k', 1850, 2150)
comp('Device:C', 'C_PH', '1uF', 2300, 2050)
comp('Device:C', 'C_ADC_100N', '100nF', 3300, 2200)
comp('Device:C', 'C_ADC_1U', '1uF', 3600, 2200)
comp('Device:LED', 'LED_AER', 'AERATOR_STATUS', 9050, 5200)
comp('Device:LED', 'LED_PWR', '3V3_OK', 9050, 6500)
comp('Transistor_BJT:Q_NPN_BEC', 'Q1', '2N2222', 7600, 5200)
comp('Transistor_BJT:Q_NPN_BEC', 'Q2', '2N2222', 7600, 5900)
comp('Device:R', 'R_Q1', '1k', 7000, 5200)
comp('Device:R', 'R_Q2', '1k', 7000, 5900)
comp('Device:D', 'D_AER', 'Flyback/Clamp', 7600, 5550)
comp('Device:D', 'D_PUMP', 'Flyback/Clamp', 7600, 6250)

# Labels grouped by nets.
labels = [
('BATTERY+', 2100, 6350), ('VBAT_SENSE', 2900, 6025), ('GND', 3200, 6350),
('5V_SYS', 4100, 6350), ('3V3', 4600, 6350), ('SIM800_4V', 6400, 4050),
('GND', 7850, 4050), ('PH_SIGNAL', 2650, 2050), ('PH_BIAS', 2100, 2050),
('DO_SIGNAL', 2650, 3050), ('NH3_ADC', 2450, 4050), ('TEMP_1W', 2450, 4900),
('I2C_SDA', 4850, 3000), ('I2C_SCL', 4850, 3100), ('ADC_AIN0_PH', 4100, 2500),
('ADC_AIN1_DO', 4100, 2600), ('ADC_AIN2_BATT', 4100, 2700), ('ADC_AIN3_PH_BIAS', 4100, 2800),
('SD_CS', 7800, 2300), ('SD_SCK', 7800, 2400), ('SD_MOSI', 7800, 2500), ('SD_MISO', 7800, 2600),
('GSM_RX', 7850, 3950), ('GSM_TX', 7850, 3850), ('AERATOR_CMD', 7850, 5100), ('DO_PUMP_CMD', 7850, 5800),
('WATCHDOG_RESET', 4850, 3400), ('USB_JTAG_OFF', 5000, 3500),
]

# Build textual schematic header.
lines = [
'EESchema Schematic File Version 4',
'LIBS:PondGuard_M6_6',
'EELAYER 29 0',
'EELAYER END',
'$Descr A3 16535 11693',
'Sheet 1 1',
'Title "PondGuard M6.6 Unified Complete Schematic"',
'Date "2026-09-07"',
'Rev "M6.6"',
'Comp "PondGuard — Autonomous Oxygen & Nitrogen Adaptive Guard"',
'Comment1 "Reference design integrating power, AFE, ESP32-C3, GSM, MicroSD, watchdog and actuators"',
'Comment2 "Use M6.5 config/pinmap as GPIO source of truth"',
'Comment3 "Pre-PCB engineering release; exact footprints/connector ratings require final review"',
'Comment4 "Aerator fail-safe ON; DO pump fail-safe OFF"',
'$EndDescr',
]

# Notes / blocks
texts = [
(800,850,'POWER / PROTECTION'),(800,1350,'pH HIGH-Z AFE'),(800,2700,'DO AFE'),(800,3750,'NH3 GAS INTERFACE'),(800,4650,'TEMPERATURE'),
(3000,1250,'ADS1115 16-BIT ANALOG ACQUISITION'),(5000,1250,'ESP32-C3 MCU'),(7600,1250,'COMMUNICATIONS / STORAGE'),(7300,4950,'ACTUATOR DRIVER STAGES'),
(800,5550,'2S Li-ion / Solar system feeds F1/TVS and downstream regulators'),
(5050,7150,'M6.6 ENGINEERING NOTES'),
(5050,7450,'1) GPIO2/8/9 intentionally unused (strapping pins).'),
(5050,7650,'2) GPIO12-17 reserved for internal flash/PSRAM interface.'),
(5050,7850,'3) GPIO18/19 used for MicroSD SPI; USB-JTAG is sacrificed in GPIO mode.'),
(5050,8050,'4) ADS1115 AIN0=pH signal, AIN1=DO, AIN2=battery, AIN3=pH bias.'),
(5050,8250,'5) SEN0567 stays on ESP32-C3 GPIO5 with 1k/100nF protection/filter.'),
(5050,8450,'6) SIM800L gets dedicated ~4.0V high-current rail; local bulk capacitance required.'),
(5050,8650,'7) MCU GPIO0/1 only drive external NPN/SSR interface stages; never mains directly.'),
(5050,8850,'8) Aerator is fail-safe environmental actuator; DO circulation pump defaults OFF.'),
(5050,9050,'9) NH3 SEN0567 is qualitative; no direct dissolved-NH3 conversion without chamber calibration.'),
(5050,9250,'10) Exact regulator, BMS, PV, SSR, connector and PCB footprints remain procurement/fab review items.'),
]

for x,y,t in texts:
    lines += [f'Text Notes {x} {y} 0    80   ~ 16', t]
for t, x,y in labels:
    lines += [f'Text Label {x} {y} 0    50   ~ 0', t]

# Place components
for lib, ref, value, x, y, orient, footprint, fields in comps:
    lines += ['$Comp', f'L {lib} {ref}', f'U 1 1 0{x}{y}', f'P {x} {y}']
    lines += [f'F 0 "{ref}" H {x+100} {y+100} 50  0000 C CNN',
              f'F 1 "{value}" H {x+200} {y-100} 50  0000 C CNN']
    if footprint:
        lines.append(f'F 2 "{footprint}" H {x} {y} 50  0001 C CNN')
    lines.append(f'\t{orient}')
    lines.append('$EndComp')

# Functional wiring (net-labelled, concise but explicit)
wires = [
# Power input + divider
(1800,6350,2350,6350),(2550,6350,2750,6350),(2950,6350,3400,6350),
(2900,5700,2900,5550),(2900,5550,2900,5350),(2900,6000,2900,6100),(2900,6300,2900,6350),
# pH bias divider and signal
(1850,1550,1850,1450),(1850,1450,2100,1450),(1850,1850,1850,2000),(1850,2300,1850,2400),
(1100,2050,1450,2050),(1450,2050,2650,2050),(2050,2050,2050,1700),(2050,1700,1850,1700),(2050,2050,2050,2150),(2050,2150,1850,2150),
(2300,1900,2300,1700),(2300,1700,2650,1700),(2300,2200,2300,2350),
# DO connector to ADC label
(1100,3050,2650,3050),(2650,3050,3150,3050),(3150,3050,3150,2600),(3150,2600,3500,2600),
# NH3 filter
(1100,4050,1450,4050),(1650,4050,1950,4050),(1950,4050,2450,4050),(1850,3900,1850,3750),(1850,3750,2200,3750),
# temp
(1100,4900,1550,4900),(1550,4750,1550,4600),(1550,5050,1550,5150),(1550,4900,2450,4900),
# ADC power and signals
(3300,2200,3300,2050),(3300,2050,3600,2050),(3600,2350,3600,2150),
(3500,2500,3150,2500),(3500,2600,3150,2600),(3500,2700,3150,2700),(3500,2800,3150,2800),
# MCU I2C / UART / SPI / actuators via labels
(4950,3000,5200,3000),(4950,3100,5200,3100),(4950,3400,5200,3400),(4950,3500,5200,3500),
(6100,2850,7800,2850),(6100,2950,7800,2950),(6100,3050,7800,3050),(6100,3150,7800,3150),
(6100,3950,7850,3950),(6100,3850,6900,3850),(6900,3850,6900,3650),(7100,3650,7300,3650),(7300,3650,7850,3650),
(6900,4050,6500,4050),(7300,4050,6500,4050),(6500,4050,6500,4050),
# SD connector
(8300,2400,7800,2400),(8300,2500,7800,2500),(8300,2600,7800,2600),(8300,2300,7800,2300),
# Actuator drivers
(7000,5200,6800,5200),(7200,5200,7450,5200),(7750,5200,7850,5200),(7600,5050,7600,4950),(7600,5350,7600,5450),(7600,5650,7600,5750),
(7000,5900,6800,5900),(7200,5900,7450,5900),(7750,5900,7850,5900),(7600,5750,7600,5450),(7600,6050,7600,6150),
# LEDs
(9050,5050,9050,4950),(9050,5350,9050,5450),(9050,4900,9050,4800),(9050,5100,9050,5200),
# power rails to modules
(4100,6350,4100,2050),(4600,6350,4600,2050),(6400,4050,6400,4250),(3400,6350,3400,6500),
]
for x1,y1,x2,y2 in wires:
    lines += [f'Wire Wire Line', f'\t{x1} {y1} {x2} {y2}']

# Add GND rails and explicit MCU pin allocation table as notes.
lines += [
'Text Notes 5000 9650 0    60   ~ 12',
'M6.5 GPIO MAP: 0 AERATOR | 1 DO_PUMP | 3 SD_CS | 4 DS18B20 | 5 NH3 | 6 I2C_SDA | 7 I2C_SCL | 10 SD_SCK | 18 SD_MOSI | 19 SD_MISO | 20 GSM_RX | 21 GSM_TX',
'Text Notes 5000 9850 0    60   ~ 12',
'ADC MAP: AIN0 PH_SIGNAL | AIN1 DO_SIGNAL | AIN2 VBAT_SENSE | AIN3 PH_BIAS',
'$EndSCHEMATC'
]
OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(OUT)
