# FPGA Fmax study — method, verified result and acceptance criteria

**Verified 20 Nov 2026:** software-estimated **93.22 MHz**, post-route path period **10.73 ns**, on a registered BPU timing harness mapped to **iCE40HX8K-CT256**. The 25 MHz requested goal was met. Mapped primitives: **427 LUT4**, **279 FF**, **56 carry**, **4 embedded RAM**. [Immutable run](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44777766230); [pinned evidence summary](../evidence/fpga_timing/POSTROUTE_RESULT.md). This is **not** a physical board measurement. Faculty approval is still pending.

This is a **new, board-less implementation study**. It does not change the
original `rtl/branch_prediction_unit.v` or the P1–P4 prediction logic.

## What this workflow measures

1. Register the BPU inputs and observed outputs in
   `rtl/fpga_timing_harness.v` so nextpnr sees real clock-to-register and
   register-to-register setup paths.
2. Verify original integrated BPU behavior using `make test-bpu`.
3. Map RTL to actual **Lattice iCE40HX8K** FPGA primitives with Yosys
   `synth_ice40 -flatten`.
4. Place and route for the **iCE40HX8K-CT256** device/package with
   `nextpnr-ice40 --hx8k --package ct256 --freq 25`.
5. Extract the **last** clock Fmax reported by nextpnr after successful route,
   verify mapped FPGA LUT/flip-flop resources, and preserve JSON, ASC, raw
   logs, tool versions and per-file SHA-256 digests.

The 25 MHz goal is **a chosen implementation target**, not a pre-established
Fmax. The actual post-route estimate is supplied ONLY by nextpnr's observed
report. `--timing-allow-fail` allows us to publish a lower achieved Fmax
honestly if the 25 MHz goal was not met. No MHz is invented.

## Commands

Ubuntu 24.04 or equivalent:

```bash
sudo apt-get update
sudo apt-get install -y iverilog yosys nextpnr-ice40 python3
make test-bpu
python3 -m unittest discover -s tests -p test_fpga_timing.py -v
bash scripts/run_fpga_timing.sh
cat results/fpga_timing/report.md
```

GitHub Actions workflow: `.github/workflows/fpga-timing.yml`. On success the
downloadable evidence artifact is named
`BPU-iCE40HX8K-Fmax-Postroute-Estimate`.

## Limitations important in the 24 November viva

- **Software estimated, not physically measured.** No FPGA board was programmed,
  no live oscillator / oscilloscope reading, and no board-specific power,
  thermal or clock constraints were used.
- **Registered harness, not the raw top or complete CPU.** Input/output
  sampling registers were introduced specifically to constrain internal BPU
  paths. The observed Fmax is an estimate for the mapped harness, not a
  guarantee about an integrated CPU running a program.
- **No real board PCF/pin mapping.** Unconstrained pins are auto-placed. The
  design includes a single clock domain; external arrival/output delay
  constraints and physical board routing are not modeled.
- **Tool-dependent.** Estimated Fmax and mapped resource counts may change with
  versions, placement seed, package and clock constraints.
- **Independent technical approval is still needed.** The course instructor
  must confirm whether this method meets the requirement for Fmax.

Do not mislabel this estimate as measured board Fmax, full-CPU throughput,
or a replacement for the separately verified 130-branch accuracy results.

## Source references

- [Original Yosys + nextpnr approach](https://github.com/YosysHQ/nextpnr)
- [Original Project IceStorm device table](https://prjicestorm.readthedocs.io/en/latest/overview.html)
- [Original BPU verification contract](BPU_RELEASE_SIGNOFF.md)
