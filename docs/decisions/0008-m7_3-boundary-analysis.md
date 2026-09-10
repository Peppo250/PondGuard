# Decision 0008 — M7.3 Boundary Analysis

## Context

M7.2 established nominal electrical reference models. Before treating the design as stable, passive tolerance, temperature, battery-voltage, and GSM transient sensitivity need to be quantified.

## Decision

Use deterministic uniform tolerance sweeps plus fixed-seed Monte-Carlo-style sampling. Keep screening limits explicit and avoid presenting them as vendor guarantees.

## Consequences

The analysis produces reproducible distributions and identifies weak boundaries. In particular, the GSM rail requires more than a nominal 2,200 µF ideal capacitor if a full 1 ms / 2 A pulse must remain above 3.4 V from a 4.0 V starting point. This is a design-review flag for M7.4, not a final capacitor selection.
