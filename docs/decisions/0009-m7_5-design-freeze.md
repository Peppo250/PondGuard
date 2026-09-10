# ADR 0009 — M7.5 Design-Freeze Candidate

## Decision
Freeze the **simulation architecture and validated electrical assumptions** at M7.5 while retaining explicit procurement and CAD-release holds.

## Rationale
M7.1 provides the connection-level digital hardware simulation. M7.2 provides electrical reference models. M7.3 quantifies tolerance/boundary behavior. M7.4 refines the two critical power flags: GSM burst droop and low-battery source sag.

## Freeze candidates
- 4,700 uF GSM local bulk capacitance.
- Low-battery policy around 6.4–6.8 V OCV for the modeled high-load condition.
- >=5 A continuous BMS target.
- Existing M6.7 GPIO and ADS1115 channel mapping.

## Not frozen
- Exact BMS, PV panel, connectors, SIM800L breakout revision, and actuator-driver package.
- Fabrication-ready PCB footprints.
- Vendor-certified closed-loop regulator SPICE.
- KiCad GUI ERC/DRC completion.
