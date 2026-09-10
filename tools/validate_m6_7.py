from pathlib import Path
import csv
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    hw = yaml.safe_load((ROOT / 'config' / 'hardware.yaml').read_text())
    assert hw['project']['version'] == '0.1.0-m6.7'
    assert hw['buses']['i2c']['sda'] == 6 and hw['buses']['i2c']['scl'] == 7
    assert hw['buses']['spi']['sck'] == 10
    assert hw['buses']['spi']['miso'] == 19 and hw['buses']['spi']['mosi'] == 18
    assert hw['communications']['gsm']['tx_pin'] == 21 and hw['communications']['gsm']['rx_pin'] == 20
    assert hw['actuators']['aerator']['fail_safe'] == 'ON'
    assert hw['actuators']['do_circulation_pump']['fail_safe'] == 'OFF'
    csv_path = ROOT / 'hardware' / 'bom' / 'M6_7_BOM.csv'
    with csv_path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    frozen = {r['Ref']: r for r in rows if r['Status'] == 'FROZEN'}
    assert frozen['U8']['MPN_or_Selection'] == 'LMR51430XFDDCR'
    assert frozen['U9']['MPN_or_Selection'] == 'LMR51430XFDDCR'
    assert frozen['U10']['MPN_or_Selection'] == 'LMR51430XFDDCR'
    assert frozen['U2']['MPN_or_Selection'] == 'ADS1115IDGSR'
    print('M6.7 validation: PASS')

if __name__ == '__main__':
    main()
