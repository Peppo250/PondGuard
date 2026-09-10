# ADR 0001 — Code-first development

## Decision

Use repository configuration, interfaces, simulation models, and automated tests as the primary engineering artifacts. Treat Wokwi and KiCad as downstream representations rather than the source of truth.

## Reason

PondGuard contains multiple representations of the same system:
- firmware
- sensor simulation
- electrical schematic
- Wokwi circuit
- documentation

A code-first source of truth reduces drift between them and makes iterative work with coding agents reproducible.

## Consequence

Hardware changes must begin in configuration and be propagated through automated tooling in later milestones.
