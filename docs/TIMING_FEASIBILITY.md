# Timing feasibility: BTB

## Status
Fmax: **UNMEASURED**. No trustworthy frequency can be stated yet.

## Why no number is given
- No FPGA device (family, part, package, speed grade), place-and-route tool or
  clock/I/O constraint set has been specified.
- Yosys generic synthesis (2404 cells) is not mapped to a device and gives no timing.
- The 10 ns clock in the testbenches (`always #5 clk = ~clk`) is a simulation
  convention. It is not a frequency target and says nothing about achievable speed.

## What is known
- Tools used so far: Icarus Verilog 13.0, Yosys 0.70 (generic synthesis only).
- Structure of the default configuration: 16 entries of (1 + 26 + 32) bits in
  registers, with a combinational lookup path (index decode, 26-bit tag
  comparator, 16:1 selection, output gating).
- Reproduce synthesis: `make synth-btb-checked`. Log: `evidence/btb_logs/btb_synthesis_checked.log`.

## Question for faculty
"Which FPGA device (family, part, package, speed grade) and toolchain (with
version) should we use for timing, and which clock and I/O constraints apply?
If none is mandated, may we report Fmax as unmeasured?"

## Reproducible path once a target is known
1. Install the specified toolchain and record its version.
2. Provide a constraint file with the clock period and I/O constraints.
3. Run synthesis and place-and-route for the named device.
4. Save the timing report (worst slack and Fmax) under `evidence/`.
5. Replace the status above with the measured value and the exact commands used.
