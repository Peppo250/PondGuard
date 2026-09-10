# ADR 0002 — Synthetic experiment baseline

## Decision

Use deterministic, seeded synthetic scenarios as the initial M3 evaluation
environment.

## Reason

PondGuard does not yet have a representative field dataset sufficient for
training or benchmarking a data-driven controller. A seeded synthetic suite
allows software behavior to be tested repeatedly without pretending simulated
data is field data.

## Consequence

M3 metrics are software validation metrics only. They must not be presented
as sensor accuracy, field detection rate, or aquaculture efficacy.
