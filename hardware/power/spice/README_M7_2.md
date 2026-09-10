# M7.2 Power Simulation Boundary

The selected LMR51430 is treated as the regulator primitive in the design review. TI specifies
4.5-36 V input and 3 A continuous output capability. The M7.2 numerical model therefore focuses
on load/power-budget screening rather than inventing an undocumented switching model.

The GSM transient netlist is intentionally lumped: battery/source impedance + bulk capacitor + load.
Use a vendor SPICE model or bench-validated regulator transient model before declaring rail droop acceptable.
