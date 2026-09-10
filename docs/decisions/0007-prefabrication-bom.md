# ADR 0007 — Pre-Fabrication BOM Freeze Candidate

## Decision

Freeze the regulator/ADC family around currently active vendor parts while keeping module-level components as procurement holds until the exact bought variants are confirmed.

## Frozen candidates

- 5 V buck: TI LMR51430XFDDCR
- 3.3 V buck: TI LMR51430XFDDCR
- 4.0 V GSM buck: TI LMR51430XFDDCR
- ADC: TI ADS1115IDGSR
- Charger controller: Consonance CN3722, package/lot to be confirmed against supplier documentation

## Rejected for new design

- MP2307 is marked **NRND / not recommended for new designs** by Monolithic Power Systems; it remains acceptable only as a legacy/prototype reference.
- AMS1117 is not used for the main 3.3 V system rail because the M6.7 architecture favors a switching regulator with higher available current and lower heat loss from the 2S source.

## Open procurement holds

Exact MPN must be selected from the physically procured lot for:

- 2S BMS/protection + balancing
- 5 W+ solar panel with Vmp >= 7.5 V
- SIM800L breakout/module revision
- SSR/relay driver stage
- MicroSD socket
- connectors, fuse holders, TVS, cable glands, and PCB footprints

## Rationale

The point of M6.7 is to prevent false precision: a fabricated design should not pretend that a generic online module is a fixed MPN. Parts whose electrical identity is already source-verifiable are frozen; module-dependent items remain explicit holds.
