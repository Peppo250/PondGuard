# PondGuard M6.1 — Power Architecture

## Status

**Design correction required before hardware assembly.**

The original project concept used:
- 5 W / 6 V solar panel
- CN3791 MPPT charger
- 2S Li-ion battery

This combination is electrically inconsistent:

1. CN3791 is a **single-cell** Li-ion charger with a 4.2 V regulation voltage.
2. The proposed battery is a **2S pack** with nominal 7.4 V and 8.4 V full-charge voltage.
3. Therefore CN3791 must not be used as a direct 2S charger.
4. A candidate replacement is CN3722, which supports single- or multi-cell Li-ion and sets the charge voltage with an external divider.
5. CN3722 requires 7.5–28 V input, so the original 6 V solar-panel concept also cannot directly satisfy its input-voltage requirement.

### Proposed corrected M6.1 architecture

```text
        PV MODULE
   Vmp >= 7.5 V
   (5 W target retained)
             |
          fuse / TVS
             |
             v
       CN3722 MPPT
             |
      2S charge path
             |
             v
     2S Li-ion BMS/protection
             |
        7.4 V nominal
        8.4 V full
             |
      +------+------+
      |             |
      v             v
  5 V BUCK        3.3 V REGULATOR
      |             |
      |             +--> ESP32-C3
      |             +--> ADS1115
      |             +--> analog front-end
      |             +--> sensors
      |
      +--> GSM / other 5 V loads

  Dedicated GSM rail:
  5 V -> ~4.0 V high-current regulator -> SIM800L
```

## Important battery-management note

A 2S pack should use a proper cell-protection/BMS arrangement with cell-level
monitoring/balancing. The charger IC alone should not be assumed to provide
cell balancing.

## Solar-module design target

For a 5 W system, choose a PV module whose actual MPP voltage is compatible with
the selected charger. Do not order a new 6 V panel for the CN3722 path.

The exact PV part number is intentionally not frozen in M6.1 because the panel
electrical datasheet must be matched to:
- CN3722 input requirements
- charger dropout/headroom
- desired charge current
- enclosure area
- solar conditions

## Rail partition

### Battery rail

`BAT+` = 2S Li-ion pack, nominal 7.4 V, full charge 8.4 V.

### 5 V rail

Use a synchronous buck regulator rated above the expected peak system load.

The existing design selected MP2307. It is electrically capable of operating
from 4.75–23 V and up to 3 A, but the manufacturer now marks MP2307 as
**not recommended for new designs** and recommends a newer alternative.

For the prototype, the repository retains MP2307 as the reference part for
continuity, but M6.1 flags it for replacement before production PCB release.

### 3.3 V rail

The existing design used AMS1117-3.3 from 5 V to 3.3 V.

This is electrically straightforward from a 5 V rail, but it is not an ideal
low-power choice because an AMS1117-class regulator has substantial quiescent
current and heat dissipation relative to a modern low-Iq regulator.

For a solar/battery design, M6.1 recommends evaluating a lower-Iq 3.3 V LDO
before production.

### GSM rail

SIM800L requires approximately 3.4–4.4 V, recommends about 4.0 V, and can draw
up to about 2 A in transmit bursts. A dedicated 4.0–4.1 V regulator/rail with
local bulk capacitance is therefore preferred over feeding the modem directly
from the 5 V rail.

## M6.1 engineering rule

Do not fabricate the power board until the following are frozen:

- PV Vmp/Voc/Isc
- CN3722 charge current
- 2S BMS/protection device
- 5 V buck part
- 3.3 V regulator
- GSM regulator and peak-current capability
- fuse/protection ratings
