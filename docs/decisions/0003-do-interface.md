# ADR 0003 — DO sensor signal interface

## Decision

Use the complete SEN0237-A conditioner as the first prototype interface.
Maintain the bare-probe TIA as a separate research branch.

## Rationale

The SEN0237-A already supplies a conditioned 0–3 V analog output. A second
TIA after that output would be redundant and would change the intended signal
chain.

## Research branch

The custom TIA remains useful if the research implementation intentionally
uses a bare galvanic probe or bypasses the vendor conditioner.

## Consequence

The firmware sensor abstraction must support calibrated voltage-to-DO
conversion without assuming the source is always a raw probe current.
