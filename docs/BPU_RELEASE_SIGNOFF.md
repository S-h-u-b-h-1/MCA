# BPU integration and final QA signoff

The original P1 (2-bit BHT), P2 (tagged BTB), and P3 (next-PC/recovery)
modules remain **unchanged**. `rtl/branch_prediction_unit.v` connects these
interfaces into a synthesizable prediction subsystem, not a full CPU or a
complete pipeline.

## Contract

- Fetch PC performs combinational BHT/BTB lookup. A predicted taken target is
  usable only if the BTB tag hits; otherwise the fallback is PC+4.
- The caller must retain the branch's original fetch-time `predicted_taken`,
  `btb_hit`, and `predicted_target` until resolution. Those saved fields are
  supplied as `resolve_predicted_*` (never use the newer live lookup outputs).
- `resolve_valid=0` denotes a bubble or squashed branch. No training or
  redirect is allowed. The direction BHT trains on valid resolved outcomes.
  The BTB trains only for **valid taken** branches.
- A redirect overrides any simultaneous speculative fetch selection.
- Reset is active-high and synchronous. Pipeline registers and instruction-kill
  distribution are deliberately outside this subsystem.

## Reproduce the tests

```bash
make test-bpu
make test
make synth-all
make metrics test-p5-metrics
git diff --exit-code -- evidence/metrics/
```

`make test-bpu` runs at INDEX_BITS=4 and 5 (16 and 32 entries).
It checks reset, taken/NT training, correct direction+target, wrong target,
BTB misses/aliased tag replacement, invalid/squashed-branch gating,
saved metadata with a simultaneous unrelated fetch, and redirect priority.
Icarus tests fail nonzero if any assertion fails.

`make synth-all` includes the new wrapper as a seventh generic synthesis
top. The BPU integration run [42200408998](https://github.com/S-h-u-b-h-1/MCA/actions/runs/42200408998) passed 70 checks for each of 16-entry and 32-entry configurations (140 total). Seven-top generic synthesis passed in [CI run 42200408851](https://github.com/S-h-u-b-h-1/MCA/actions/runs/42200408851); the retained artifact was inspected against its JSON netlists and source-hash manifest. The committed summary records the verified Yosys 0.33 numbers, including 2,993 generic cells for the integrated wrapper. These are not device-mapped resources or Fmax.

## Faculty submission is still not finished

- Confirm all five author names, affiliation details and section approvals.
- Assemble and visually inspect `report/Phase1_IEEE_Report.pdf` in IEEE format.
- Record and edit a genuine 4:30–4:50 demonstration with all five people,
  host it accessibly and put the URL in README and `video/DEMO_LINK.md`.
- Choose an FPGA/device plus valid timing constraints and tool flow, or
  ask faculty whether the explicitly unmeasured maximum frequency is acceptable.
- Run final commands on merged `main`, verify links, submit by
  **16 November 2026, 11:59 PM IST**.

Generic Yosys cells do not establish FPGA LUT counts or maximum clock MHz.
The CPI figures are illustrative, not measured CPU speedup.
