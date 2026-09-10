# ADR 0004 — pH level-shift and dual-buffer topology

## Decision

Use an AD8607 dual op-amp:
- one channel buffers a 1.65 V bias
- one channel buffers the pH measurement electrode

Read the pH voltage differentially with the ADS1115.

## Reason

A raw pH electrode produces a bipolar signal. A single-supply ADC cannot
directly accept the negative half of that signal relative to ground.

The buffered reference-electrode bias shifts the entire electrode signal into
the valid positive supply range, while differential ADC measurement removes
the bias digitally.

One AD8603 channel can provide only one unity-gain buffer, so a single
AD8603 cannot implement both the buffered bias and buffered pH measurement
paths.

## Alternatives

- two AD8603 devices: electrically valid but larger BOM
- AD8607 dual: preferred
- dedicated pH AFE IC: not selected for M6.3 because the project explicitly
  wants a transparent, low-cost general-purpose AFE

## Consequence

The M1/M4 abstract `ph` sensor interface remains unchanged. Only its physical
implementation changes from a single-buffer concept to a dual-buffer
interface.
