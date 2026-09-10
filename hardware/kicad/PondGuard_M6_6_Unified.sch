EESchema Schematic File Version 4
LIBS:PondGuard_M6_6
EELAYER 29 0
EELAYER END
$Descr A3 16535 11693
Sheet 1 1
Title "PondGuard M6.6 Unified Complete Schematic"
Date "2026-09-07"
Rev "M6.6"
Comp "PondGuard — Autonomous Oxygen & Nitrogen Adaptive Guard"
Comment1 "Reference design integrating power, AFE, ESP32-C3, GSM, MicroSD, watchdog and actuators"
Comment2 "Use M6.5 config/pinmap as GPIO source of truth"
Comment3 "Pre-PCB engineering release; exact footprints/connector ratings require final review"
Comment4 "Aerator fail-safe ON; DO pump fail-safe OFF"
$EndDescr
Text Notes 800 850 0    80   ~ 16
POWER / PROTECTION
Text Notes 800 1350 0    80   ~ 16
pH HIGH-Z AFE
Text Notes 800 2700 0    80   ~ 16
DO AFE
Text Notes 800 3750 0    80   ~ 16
NH3 GAS INTERFACE
Text Notes 800 4650 0    80   ~ 16
TEMPERATURE
Text Notes 3000 1250 0    80   ~ 16
ADS1115 16-BIT ANALOG ACQUISITION
Text Notes 5000 1250 0    80   ~ 16
ESP32-C3 MCU
Text Notes 7600 1250 0    80   ~ 16
COMMUNICATIONS / STORAGE
Text Notes 7300 4950 0    80   ~ 16
ACTUATOR DRIVER STAGES
Text Notes 800 5550 0    80   ~ 16
2S Li-ion / Solar system feeds F1/TVS and downstream regulators
Text Notes 5050 7150 0    80   ~ 16
M6.6 ENGINEERING NOTES
Text Notes 5050 7450 0    80   ~ 16
1) GPIO2/8/9 intentionally unused (strapping pins).
Text Notes 5050 7650 0    80   ~ 16
2) GPIO12-17 reserved for internal flash/PSRAM interface.
Text Notes 5050 7850 0    80   ~ 16
3) GPIO18/19 used for MicroSD SPI; USB-JTAG is sacrificed in GPIO mode.
Text Notes 5050 8050 0    80   ~ 16
4) ADS1115 AIN0=pH signal, AIN1=DO, AIN2=battery, AIN3=pH bias.
Text Notes 5050 8250 0    80   ~ 16
5) SEN0567 stays on ESP32-C3 GPIO5 with 1k/100nF protection/filter.
Text Notes 5050 8450 0    80   ~ 16
6) SIM800L gets dedicated ~4.0V high-current rail; local bulk capacitance required.
Text Notes 5050 8650 0    80   ~ 16
7) MCU GPIO0/1 only drive external NPN/SSR interface stages; never mains directly.
Text Notes 5050 8850 0    80   ~ 16
8) Aerator is fail-safe environmental actuator; DO circulation pump defaults OFF.
Text Notes 5050 9050 0    80   ~ 16
9) NH3 SEN0567 is qualitative; no direct dissolved-NH3 conversion without chamber calibration.
Text Notes 5050 9250 0    80   ~ 16
10) Exact regulator, BMS, PV, SSR, connector and PCB footprints remain procurement/fab review items.
Text Label 2100 6350 0    50   ~ 0
BATTERY+
Text Label 2900 6025 0    50   ~ 0
VBAT_SENSE
Text Label 3200 6350 0    50   ~ 0
GND
Text Label 4100 6350 0    50   ~ 0
5V_SYS
Text Label 4600 6350 0    50   ~ 0
3V3
Text Label 6400 4050 0    50   ~ 0
SIM800_4V
Text Label 7850 4050 0    50   ~ 0
GND
Text Label 2650 2050 0    50   ~ 0
PH_SIGNAL
Text Label 2100 2050 0    50   ~ 0
PH_BIAS
Text Label 2650 3050 0    50   ~ 0
DO_SIGNAL
Text Label 2450 4050 0    50   ~ 0
NH3_ADC
Text Label 2450 4900 0    50   ~ 0
TEMP_1W
Text Label 4850 3000 0    50   ~ 0
I2C_SDA
Text Label 4850 3100 0    50   ~ 0
I2C_SCL
Text Label 4100 2500 0    50   ~ 0
ADC_AIN0_PH
Text Label 4100 2600 0    50   ~ 0
ADC_AIN1_DO
Text Label 4100 2700 0    50   ~ 0
ADC_AIN2_BATT
Text Label 4100 2800 0    50   ~ 0
ADC_AIN3_PH_BIAS
Text Label 7800 2300 0    50   ~ 0
SD_CS
Text Label 7800 2400 0    50   ~ 0
SD_SCK
Text Label 7800 2500 0    50   ~ 0
SD_MOSI
Text Label 7800 2600 0    50   ~ 0
SD_MISO
Text Label 7850 3950 0    50   ~ 0
GSM_RX
Text Label 7850 3850 0    50   ~ 0
GSM_TX
Text Label 7850 5100 0    50   ~ 0
AERATOR_CMD
Text Label 7850 5800 0    50   ~ 0
DO_PUMP_CMD
Text Label 4850 3400 0    50   ~ 0
WATCHDOG_RESET
Text Label 5000 3500 0    50   ~ 0
USB_JTAG_OFF
$Comp
L Connector_Generic:Conn_01x16 J_MCU
U 1 1 056503850
P 5650 3850
F 0 "J_MCU" H 5750 3950 50  0000 C CNN
F 1 "ESP32-C3" H 5850 3750 50  0000 C CNN
F 2 "Module:ESP32-C3-MINI-1" H 5650 3850 50  0001 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x10 J_ADC
U 1 1 036002650
P 3600 2650
F 0 "J_ADC" H 3700 2750 50  0000 C CNN
F 1 "ADS1115" H 3800 2550 50  0000 C CNN
F 2 "Package_DIP:DIP-10_W7.62mm" H 3600 2650 50  0001 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J_PH
U 1 1 011002050
P 1100 2050
F 0 "J_PH" H 1200 2150 50  0000 C CNN
F 1 "pH electrode" H 1300 1950 50  0000 C CNN
F 2 "Connector_Coaxial:BNC" H 1100 2050 50  0001 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x02 J_DO
U 1 1 011003050
P 1100 3050
F 0 "J_DO" H 1200 3150 50  0000 C CNN
F 1 "DO interface" H 1300 2950 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J_NH3
U 1 1 011004050
P 1100 4050
F 0 "J_NH3" H 1200 4150 50  0000 C CNN
F 1 "SEN0567" H 1300 3950 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J_TEMP
U 1 1 011004900
P 1100 4900
F 0 "J_TEMP" H 1200 5000 50  0000 C CNN
F 1 "DS18B20" H 1300 4800 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J_SD
U 1 1 083002500
P 8300 2500
F 0 "J_SD" H 8400 2600 50  0000 C CNN
F 1 "MicroSD" H 8500 2400 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J_GSM
U 1 1 083004050
P 8300 4050
F 0 "J_GSM" H 8400 4150 50  0000 C CNN
F 1 "SIM800L" H 8500 3950 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J_AER
U 1 1 083005200
P 8300 5200
F 0 "J_AER" H 8400 5300 50  0000 C CNN
F 1 "Aerator driver input" H 8500 5100 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x03 J_PUMP
U 1 1 083005900
P 8300 5900
F 0 "J_PUMP" H 8400 6000 50  0000 C CNN
F 1 "DO pump driver input" H 8500 5800 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J_PWR
U 1 1 018006500
P 1800 6500
F 0 "J_PWR" H 1900 6600 50  0000 C CNN
F 1 "System power" H 2000 6400 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Connector_Generic:Conn_01x04 J_SENSE_PWR
U 1 1 036006500
P 3600 6500
F 0 "J_SENSE_PWR" H 3700 6600 50  0000 C CNN
F 1 "Rails" H 3800 6400 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:Fuse F1
U 1 1 024506350
P 2450 6350
F 0 "F1" H 2550 6450 50  0000 C CNN
F 1 "1A" H 2650 6250 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:D D1
U 1 1 028506350
P 2850 6350
F 0 "D1" H 2950 6450 50  0000 C CNN
F 1 "TVS 5.1V" H 3050 6250 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_BATT_TOP
U 1 1 029005850
P 2900 5850
F 0 "R_BATT_TOP" H 3000 5950 50  0000 C CNN
F 1 "10k" H 3100 5750 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_BATT_BOT
U 1 1 029006200
P 2900 6200
F 0 "R_BATT_BOT" H 3000 6300 50  0000 C CNN
F 1 "3.3k" H 3100 6100 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:C C_GSM_BULK
U 1 1 069004050
P 6900 4050
F 0 "C_GSM_BULK" H 7000 4150 50  0000 C CNN
F 1 "100uF LOW-ESR" H 7100 3950 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:C C_GSM_LOCAL
U 1 1 073004050
P 7300 4050
F 0 "C_GSM_LOCAL" H 7400 4150 50  0000 C CNN
F 1 "4.7uF" H 7500 3950 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:C C_NH3
U 1 1 018504050
P 1850 4050
F 0 "C_NH3" H 1950 4150 50  0000 C CNN
F 1 "100nF" H 2050 3950 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_NH3
U 1 1 015504050
P 1550 4050
F 0 "R_NH3" H 1650 4150 50  0000 C CNN
F 1 "1k" H 1750 3950 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_DS_PULL
U 1 1 015504900
P 1550 4900
F 0 "R_DS_PULL" H 1650 5000 50  0000 C CNN
F 1 "4.7k" H 1750 4800 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_GSM_SER
U 1 1 069003650
P 6900 3650
F 0 "R_GSM_SER" H 7000 3750 50  0000 C CNN
F 1 "1k" H 7100 3550 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_GSM_PD
U 1 1 073003650
P 7300 3650
F 0 "R_GSM_PD" H 7400 3750 50  0000 C CNN
F 1 "10k" H 7500 3550 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_PH_TOP
U 1 1 018501700
P 1850 1700
F 0 "R_PH_TOP" H 1950 1800 50  0000 C CNN
F 1 "10k" H 2050 1600 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_PH_BOT
U 1 1 018502150
P 1850 2150
F 0 "R_PH_BOT" H 1950 2250 50  0000 C CNN
F 1 "10k" H 2050 2050 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:C C_PH
U 1 1 023002050
P 2300 2050
F 0 "C_PH" H 2400 2150 50  0000 C CNN
F 1 "1uF" H 2500 1950 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:C C_ADC_100N
U 1 1 033002200
P 3300 2200
F 0 "C_ADC_100N" H 3400 2300 50  0000 C CNN
F 1 "100nF" H 3500 2100 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:C C_ADC_1U
U 1 1 036002200
P 3600 2200
F 0 "C_ADC_1U" H 3700 2300 50  0000 C CNN
F 1 "1uF" H 3800 2100 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:LED LED_AER
U 1 1 090505200
P 9050 5200
F 0 "LED_AER" H 9150 5300 50  0000 C CNN
F 1 "AERATOR_STATUS" H 9250 5100 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:LED LED_PWR
U 1 1 090506500
P 9050 6500
F 0 "LED_PWR" H 9150 6600 50  0000 C CNN
F 1 "3V3_OK" H 9250 6400 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Transistor_BJT:Q_NPN_BEC Q1
U 1 1 076005200
P 7600 5200
F 0 "Q1" H 7700 5300 50  0000 C CNN
F 1 "2N2222" H 7800 5100 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Transistor_BJT:Q_NPN_BEC Q2
U 1 1 076005900
P 7600 5900
F 0 "Q2" H 7700 6000 50  0000 C CNN
F 1 "2N2222" H 7800 5800 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_Q1
U 1 1 070005200
P 7000 5200
F 0 "R_Q1" H 7100 5300 50  0000 C CNN
F 1 "1k" H 7200 5100 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:R R_Q2
U 1 1 070005900
P 7000 5900
F 0 "R_Q2" H 7100 6000 50  0000 C CNN
F 1 "1k" H 7200 5800 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:D D_AER
U 1 1 076005550
P 7600 5550
F 0 "D_AER" H 7700 5650 50  0000 C CNN
F 1 "Flyback/Clamp" H 7800 5450 50  0000 C CNN
	1 0 0 -1
$EndComp
$Comp
L Device:D D_PUMP
U 1 1 076006250
P 7600 6250
F 0 "D_PUMP" H 7700 6350 50  0000 C CNN
F 1 "Flyback/Clamp" H 7800 6150 50  0000 C CNN
	1 0 0 -1
$EndComp
Wire Wire Line
	1800 6350 2350 6350
Wire Wire Line
	2550 6350 2750 6350
Wire Wire Line
	2950 6350 3400 6350
Wire Wire Line
	2900 5700 2900 5550
Wire Wire Line
	2900 5550 2900 5350
Wire Wire Line
	2900 6000 2900 6100
Wire Wire Line
	2900 6300 2900 6350
Wire Wire Line
	1850 1550 1850 1450
Wire Wire Line
	1850 1450 2100 1450
Wire Wire Line
	1850 1850 1850 2000
Wire Wire Line
	1850 2300 1850 2400
Wire Wire Line
	1100 2050 1450 2050
Wire Wire Line
	1450 2050 2650 2050
Wire Wire Line
	2050 2050 2050 1700
Wire Wire Line
	2050 1700 1850 1700
Wire Wire Line
	2050 2050 2050 2150
Wire Wire Line
	2050 2150 1850 2150
Wire Wire Line
	2300 1900 2300 1700
Wire Wire Line
	2300 1700 2650 1700
Wire Wire Line
	2300 2200 2300 2350
Wire Wire Line
	1100 3050 2650 3050
Wire Wire Line
	2650 3050 3150 3050
Wire Wire Line
	3150 3050 3150 2600
Wire Wire Line
	3150 2600 3500 2600
Wire Wire Line
	1100 4050 1450 4050
Wire Wire Line
	1650 4050 1950 4050
Wire Wire Line
	1950 4050 2450 4050
Wire Wire Line
	1850 3900 1850 3750
Wire Wire Line
	1850 3750 2200 3750
Wire Wire Line
	1100 4900 1550 4900
Wire Wire Line
	1550 4750 1550 4600
Wire Wire Line
	1550 5050 1550 5150
Wire Wire Line
	1550 4900 2450 4900
Wire Wire Line
	3300 2200 3300 2050
Wire Wire Line
	3300 2050 3600 2050
Wire Wire Line
	3600 2350 3600 2150
Wire Wire Line
	3500 2500 3150 2500
Wire Wire Line
	3500 2600 3150 2600
Wire Wire Line
	3500 2700 3150 2700
Wire Wire Line
	3500 2800 3150 2800
Wire Wire Line
	4950 3000 5200 3000
Wire Wire Line
	4950 3100 5200 3100
Wire Wire Line
	4950 3400 5200 3400
Wire Wire Line
	4950 3500 5200 3500
Wire Wire Line
	6100 2850 7800 2850
Wire Wire Line
	6100 2950 7800 2950
Wire Wire Line
	6100 3050 7800 3050
Wire Wire Line
	6100 3150 7800 3150
Wire Wire Line
	6100 3950 7850 3950
Wire Wire Line
	6100 3850 6900 3850
Wire Wire Line
	6900 3850 6900 3650
Wire Wire Line
	7100 3650 7300 3650
Wire Wire Line
	7300 3650 7850 3650
Wire Wire Line
	6900 4050 6500 4050
Wire Wire Line
	7300 4050 6500 4050
Wire Wire Line
	6500 4050 6500 4050
Wire Wire Line
	8300 2400 7800 2400
Wire Wire Line
	8300 2500 7800 2500
Wire Wire Line
	8300 2600 7800 2600
Wire Wire Line
	8300 2300 7800 2300
Wire Wire Line
	7000 5200 6800 5200
Wire Wire Line
	7200 5200 7450 5200
Wire Wire Line
	7750 5200 7850 5200
Wire Wire Line
	7600 5050 7600 4950
Wire Wire Line
	7600 5350 7600 5450
Wire Wire Line
	7600 5650 7600 5750
Wire Wire Line
	7000 5900 6800 5900
Wire Wire Line
	7200 5900 7450 5900
Wire Wire Line
	7750 5900 7850 5900
Wire Wire Line
	7600 5750 7600 5450
Wire Wire Line
	7600 6050 7600 6150
Wire Wire Line
	9050 5050 9050 4950
Wire Wire Line
	9050 5350 9050 5450
Wire Wire Line
	9050 4900 9050 4800
Wire Wire Line
	9050 5100 9050 5200
Wire Wire Line
	4100 6350 4100 2050
Wire Wire Line
	4600 6350 4600 2050
Wire Wire Line
	6400 4050 6400 4250
Wire Wire Line
	3400 6350 3400 6500
Text Notes 5000 9650 0    60   ~ 12
M6.5 GPIO MAP: 0 AERATOR | 1 DO_PUMP | 3 SD_CS | 4 DS18B20 | 5 NH3 | 6 I2C_SDA | 7 I2C_SCL | 10 SD_SCK | 18 SD_MOSI | 19 SD_MISO | 20 GSM_RX | 21 GSM_TX
Text Notes 5000 9850 0    60   ~ 12
ADC MAP: AIN0 PH_SIGNAL | AIN1 DO_SIGNAL | AIN2 VBAT_SENSE | AIN3 PH_BIAS
$EndSCHEMATC
