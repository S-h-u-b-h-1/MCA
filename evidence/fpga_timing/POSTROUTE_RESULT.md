# Device-specific FPGA timing and resource evidence (20 November 2026)

**Result: SUCCESS — software post-route estimate, not a physical board measurement.**

| Field | Independently verified value |
| --- | --- |
| Target device/package | Lattice **iCE40HX8K-CT256** |
| Technology mapping | Yosys **0.33** `synth_ice40 -flatten` |
| Placement, routing and clock report | nextpnr-ice40 **0.6-3build5** |
| Top measured | `bpu_fpga_timing_top`, an I/O-registered harness around the unchanged `branch_prediction_unit` |
| **Estimated maximum internal clock** | **93.22 MHz** |
| Equivalent estimated minimum period | **10.73 ns** |
| Requested design clock target | 25.00 MHz — **PASS** |
| Mapped FPGA LUTs | **427 `SB_LUT4`** |
| Mapped flip-flops | **279** (multiple `SB_DFF*` types) |
| Carry chain primitives | **56 `SB_CARRY`** |
| Embedded RAM blocks | **4 `SB_RAM40_4K`** |
| External I/O bits | **173** |
| Route result | **Routing complete**, nextpnr normal exit, 1 warning and 0 errors |
| Tool source revision | PR #19 test commit `4bb735a6737129d00c98d8416572b5c39c1f0411` |

## Verifiable original run

- [GitHub Actions timing run #44777766230](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44777766230), all timing-job steps successful.
- [Archived Yosys/nextpnr log, mapped netlist, routed ASC, summaries, source SHA-256, tool versions and BPU test logs](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44777766230/artifacts/14648709651). Archive is retained for 90 days.
- Generated artifact: `results/fpga_timing/report.md` and `summary.json`; source SHA-256 for each RTL input is recorded there.
- To rerun: `make test-bpu && python3 -m unittest discover -s tests -p test_fpga_timing.py -v && bash scripts/run_fpga_timing.sh`.

### Critical path

The post-route **posedge-to-posedge** critical path starts at BTB tag RAM
`dut.targets.tag_r.0.0_RAM.RDATA_2`, passes through tag/BTB hit lookups
and next-PC selection, and finishes at
`selected_next_pc_w_SB_LUT4_O_21_LC.I1` (registered observed next PC).
nextpnr reported approximately **4.5 ns logic plus 6.3 ns routing** on this
path. Exact detailed path is retained in `nextpnr-route.log`.

### Distinguish three different types of evidence

1. **Functional RTL tests:** `make test-bpu` passed in the same run, including 16- and 32-entry BPU tests.
2. **Generic synthesis:** previous Yosys 0.33 summary contains **2,993 generic cells** for the integrated raw BPU. Do not compare it directly with mapped FPGA primitives.
3. **Device-targeted FPGA estimate:** this test mapped the BPU plus a thin *registered I/O timing wrapper* to actual iCE40 primitives, placed and routed it, and reported **93.22 MHz software-estimated** clock Fmax.

### Exact limitations

- A physical FPGA board was **not** programmed or measured.
- **No board-specific PCF/pinout** was supplied; nextpnr automatically placed external I/O pins.
- Primary I/O arrival/output delay constraints, pin loading, thermal/voltage variation, and CPU integration are not modeled.
- The *registered harness* is distinct from the raw BPU interface; the timing estimate is scoped to its synchronous paths.
- We cannot claim 93.22 MHz on any other FPGA, an actual installed CPU, or the university's unspecified target hardware.
- The requested **25 MHz** timing goal is an explicit software target, **not** an assumed Fmax.
- Faculty must explicitly determine whether this board-less route timing study satisfies Project 5's Fmax criterion.

For methodology, see [FPGA timing study](../../docs/FPGA_TIMING_STUDY.md). For the official original timing caveat, see [timing feasibility](../../docs/TIMING_FEASIBILITY.md).
