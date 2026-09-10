from pathlib import Path
import csv, json, re

ROOT = Path(__file__).resolve().parents[1]
SCH = ROOT / 'hardware' / 'kicad' / 'PondGuard_M6_6_Unified.sch'
PINMAP = ROOT / 'config' / 'pinmap_m6_5.json'


def test_schematic_exists_and_has_expected_blocks():
    text = SCH.read_text(encoding='utf-8')
    for token in ['PondGuard M6.6 Unified Complete Schematic', 'POWER / PROTECTION',
                  'ADS1115 16-BIT ANALOG ACQUISITION', 'ESP32-C3 MCU',
                  'COMMUNICATIONS / STORAGE', 'ACTUATOR DRIVER STAGES']:
        assert token in text


def test_pinmap_is_preserved():
    data = json.loads(PINMAP.read_text(encoding='utf-8'))
    expected = {
        'AERATOR_DRIVER': 0, 'DO_PUMP_DRIVER': 1, 'SD_CS': 3, 'DS18B20': 4,
        'NH3_ADC': 5, 'I2C_SDA': 6, 'I2C_SCL': 7, 'SD_SCK': 10,
        'SD_MOSI': 18, 'SD_MISO': 19, 'GSM_RX': 20, 'GSM_TX': 21,
    }
    signals = {row['signal']: row['gpio'] for row in data['assignments']}
    assert signals == expected


def test_adc_allocation_is_documented():
    text = SCH.read_text(encoding='utf-8')
    for token in ['ADC_AIN0_PH', 'ADC_AIN1_DO', 'ADC_AIN2_BATT', 'ADC_AIN3_PH_BIAS']:
        assert token in text


def test_required_m6_6_safety_notes_present():
    text = SCH.read_text(encoding='utf-8')
    required = [
        'Aerator is fail-safe environmental actuator',
        'SEN0567 is qualitative',
        'SIM800L gets dedicated ~4.0V high-current rail',
        'GPIO2/8/9 intentionally unused',
        'GPIO12-17 reserved',
    ]
    for token in required:
        assert token in text
