EESchema Schematic File Version 4
LIBS:power
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
Sheet 1 1
Title "PondGuard M6.1 Power Architecture - PRELIMINARY"
Comment1 "2S solar power subsystem"
Comment2 "CN3722 selected for multi-cell concept; verify datasheets before fabrication"
Comment3 "PV module must meet charger input requirements"
Comment4 "NOT FOR FABRICATION"
$EndDescr
Text Notes 900 900 0 100 ~ 20
PONDGUARD M6.1 POWER SUBSYSTEM
Text Notes 900 1200 0 60 ~ 12
PRELIMINARY: CN3791 removed because it is single-cell. CN3722 requires PV input >=7.5V.
Text Notes 900 1600 0 70 ~ 12
PV MODULE
Text Notes 2400 1600 0 70 ~ 12
CN3722 MPPT / CC-CV
Text Notes 4700 1600 0 70 ~ 12
2S Li-ion + BMS
Text Notes 7000 1600 0 70 ~ 12
5V BUCK
Text Notes 9000 1600 0 70 ~ 12
3.3V LDO
Text Notes 900 3000 0 70 ~ 12
5W target; select PV Vmp/Voc/Isc from datasheet
Text Notes 2400 3000 0 70 ~ 12
CV = 8.4V pack target; RCS sets charge current
Text Notes 4700 3000 0 70 ~ 12
Cell-level protection + balancing required
Text Notes 7000 3000 0 70 ~ 12
Reference MP2307; replace before production
Text Notes 9000 3000 0 70 ~ 12
Reference AMS1117-3.3; evaluate lower-Iq LDO
Text Notes 7000 4200 0 70 ~ 12
Dedicated GSM regulator: ~4.0V, peak >=2A
Text Notes 900 5000 0 60 ~ 12
Safety: fuse/TVS/reverse-polarity/protection values remain TBD until final components are selected.
$EndSCHEMATC
