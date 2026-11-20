# FPGA timing feasibility — BTB and integrated BPU

## Status after 20 November 2026

**Software-estimated routed Fmax: 93.22 MHz** for a *registered wrapper around the unchanged integrated BPU* mapped to **Lattice iCE40HX8K-CT256** with Yosys 0.33 and nextpnr 0.6. The explicitly requested 25 MHz clock target was met. The device-mapped result uses 427 LUT4s, 279 flip-flops, 56 carry primitives and 4 embedded RAM blocks. [See pinned raw timing evidence](../evidence/fpga_timing/POSTROUTE_RESULT.md).

**Physical-board operating frequency remains UNMEASURED.** The university has not specified a board/pinout or timing constraints, and no physical FPGA was programmed. The estimate has not received faculty acceptance as satisfying the course hardware-frequency requirement.

## Why physical Fmax cannot yet be claimed
- The new study selects an **example FPGA target for software analysis**, not a faculty-assigned development board. Primary input/output timing and board pins are unconstrained.
- An earlier Yosys BTB generic synthesis (2404 cells) had no device timing. The new HX8K report is a separate mapped **BPU timing wrapper**, not an equivalent cell-count comparison.
- The 10 ns clock in the testbenches (`always #5 clk = ~clk`) is simulation stimulus, not a measured hardware clock or proof of 100 MHz.

## What is known
- Tools used so far: Icarus Verilog 13.0, Yosys 0.70 (generic synthesis only).
- Structure of the default configuration: 16 entries of (1 + 26 + 32) bits in
  registers, with a combinational lookup path (index decode, 26-bit tag
  comparator, 16:1 selection, output gating).
- Reproduce synthesis: `make synth-btb-checked`. Log: `evidence/btb_logs/btb_synthesis_checked.log`.

## Question for faculty
"We verified 93.22 MHz as a **software post-route estimate** for our registered BPU harness on iCE40HX8K-CT256, supported by CI logs and primitive counts. Will that device-targeted estimate satisfy the Phase II Fmax criterion? If not, which exact FPGA device/board, package/speed grade, toolchain, clock, pins and input/output timing constraints should we use? We will continue to label **physical Fmax unmeasured** until actual hardware testing or explicit approval."

## Reproducible path once a target is known
1. Install the specified toolchain and record its version.
2. Provide a constraint file with the clock period and I/O constraints.
3. Run synthesis and place-and-route for the named device.
4. Save the timing report (worst slack and Fmax) under `evidence/`.
5. Replace the status above with the measured value and the exact commands used.

## Primary post-route evidence

- [GitHub Actions successful run](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44777766230)
- [Full routed evidence and critical path](../evidence/fpga_timing/POSTROUTE_RESULT.md)
- Reproduce: `bash scripts/run_fpga_timing.sh` after installing Yosys and nextpnr-ice40.
