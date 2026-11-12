# P3 — Pipeline Control: Next-PC Selection, Branch Resolution, and BPU Subsystem Integration

**Author:** Tanmay Singh (Person 3: Next-PC Selection, Branch Resolution, and Control Integration)
**Date:** 8 November 2026 (Updated for BPU Release Signoff & Issue #9)
**Status:** Subsystem-level integration synthesized and verified (`rtl/branch_prediction_unit.v`); physical CPU pipeline registers and full processor datapath are out-of-scope for Phase I prototype.

---

## 1. Overview

This document describes the combinational pipeline control modules and their integration into the top-level Branch Prediction Unit:

| Module | File | Role & Purpose |
|---|---|---|
| `next_pc_mux` | `rtl/next_pc_mux.v` | Speculative fetch-stage next-PC selection |
| `branch_resolution` | `rtl/branch_resolution.v` | Execute-stage misprediction detection and recovery signal generation |
| `branch_prediction_unit` | `rtl/branch_prediction_unit.v` | Synthesizable top-level wrapper combining P1 BHT, P2 BTB, and P3 Control |

These modules bridge the P1 direction predictor (`predictor_2bit`) and P2 target predictor (`branch_target_buffer`), converting prediction status and execution outcomes into pipeline control strobes (`flush`, `redirect`, `redirect_pc`, `selected_next_pc`).

> [!IMPORTANT]
> **Subsystem Boundary vs. Complete CPU:**
> The `branch_prediction_unit` module is a fully synthesizable **branch-prediction subsystem and recovery controller**, not a complete five-stage pipelined CPU. It generates the architectural recovery interface (`flush` and `redirect`) that a full processor pipeline would consume. Surrounding CPU structures—such as physical inter-stage pipeline registers (IF/ID, ID/EX, EX/MEM), instruction/data caches, ALU branch condition generation, and register files—are modeled via deterministic verification testbenches (`tb_integrated.sv`, `tb_branch_prediction_unit.sv`).

---

## 2. Architecture and Data Flow

```
  ┌─────────────────────────── BRANCH PREDICTION SUBSYSTEM ──────────────────────────┐
  │                                                                                   │
  │   fetch_pc ───┬──► P1 BHT (predictor_2bit) ──► predicted_taken                   │
  │               │                                      │                            │
  │               ├──► P2 BTB (branch_target_buffer) ────┼──► btb_hit                 │
  │               │                                      │    predicted_target        │
  │               │                                      │       │                    │
  │               └──► next_pc_mux ◄─────────────────────┴───────┘                    │
  │                         │                                                         │
  │                  predicted_next_pc                                                │
  │                         │                                                         │
  │                         ▼                                                         │
  │   selected_next_pc ◄── Top MUX ◄── redirect                                       │
  │                         ▲                                                         │
  │                         │ redirect_pc                                             │
  │                         │                                                         │
  │   ┌─────────────────────┴─────────────────────────────────────────────────────┐   │
  │   │ branch_resolution (Execute Stage)                                         │   │
  │   │                                                                           │   │
  │   │ Inputs:  Saved fetch metadata: {branch_pc, pred_taken, btb_hit, target}   │   │
  │   │          Actual execution outcome: {resolve_valid, actual_taken, target}  │   │
  │   │ Outputs: mispredict, flush, redirect, redirect_pc                         │   │
  │   └───────────────────────────────────────────────────────────────────────────┘   │
  │                                                                                   │
  └───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Next-PC Selection Truth Table

The `next_pc_mux` module operates combinationally in the fetch stage:

| `predicted_taken` | `btb_hit` | `predicted_next_pc` | Architectural Rationale |
|:-:|:-:|---|---|
| 0 | 0 | `pc + 4` | Not-taken prediction → sequential fetch |
| 0 | 1 | `pc + 4` | Not-taken prediction → sequential fetch (BTB hit ignored) |
| 1 | 0 | `pc + 4` | Taken but BTB miss → conservative fallback; recovered at resolution |
| 1 | 1 | `predicted_target` | Taken with valid cached target → speculative redirect |

---

## 4. Branch Resolution Truth Table

Evaluated during branch execution when `valid = 1`. When `valid = 0` (e.g. non-branch instruction or squashed cycle), all recovery strobes are deasserted.

| # | `pred_taken` | `btb_hit` | `pred_target` | `actual_taken` | `actual_target` | `mispredict` | `redirect_pc` | Classification |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|---|---|
| 1 | 0 | × | × | 0 | × | 0 | — | Correct: Not-Taken |
| 2 | 1 | 1 | T | 1 | T | 0 | — | Correct: Taken + Target Hit |
| 3 | 0 | × | × | 1 | A | 1 | A | Direction Mispredict: NT → Taken |
| 4 | 1 | × | × | 0 | × | 1 | `branch_pc + 4` | Direction Mispredict: Taken → NT |
| 5 | 1 | 0 | × | 1 | A | 1 | A | BTB Miss on Taken Branch |
| 6 | 1 | 1 | T≠A | 1 | A | 1 | A | Target Mispredict: Cached target mismatch |

**Legend:** `T` = predicted target, `A` = actual target, `×` = don't care, `—` = deasserted.

### Formal Misprediction Equation

$$\text{Mispredict} = \text{Valid} \land \Big( (P_{taken} \neq A_{taken}) \lor \big( A_{taken} \land (\neg BTB_{hit} \lor (Target_{pred} \neq Target_{actual})) \big) \Big)$$

---

## 5. Signal Timing and Metadata Preservation

### Why Save Metadata at Fetch Time?
The BHT and BTB are dynamically updated by every retiring branch. Between the cycle a branch is fetched and speculative next-PC computed, and the cycle that branch reaches the execute stage, other intervening branches may execute and update table entries.

Comparing execution results against the *live* table state would cause false mispredictions due to race conditions or intervening updates. Therefore, the pipeline registers must preserve:
1. `branch_pc`: The instruction address of the resolving branch.
2. `predicted_taken`: The direction prediction captured at fetch.
3. `btb_hit`: Whether the BTB hit during fetch.
4. `predicted_target`: The target address provided by the BTB at fetch.

The `branch_resolution` module accepts these saved signals directly, ensuring deterministic comparison.

---

## 6. Port Specifications

### `next_pc_mux` (Combinational)

| Port | Dir | Width | Description |
|---|:-:|:-:|---|
| `pc` | in | 32 | Current fetch program counter |
| `predicted_taken` | in | 1 | P1 BHT direction prediction |
| `btb_hit` | in | 1 | P2 BTB valid tag match |
| `predicted_target` | in | 32 | P2 BTB predicted target address |
| `predicted_next_pc` | out | 32 | Speculatively selected next PC |

### `branch_resolution` (Combinational)

| Port | Dir | Width | Description |
|---|:-:|:-:|---|
| `valid` | in | 1 | Branch resolution valid strobe in execution stage |
| `branch_pc` | in | 32 | Program counter of resolving branch |
| `predicted_taken` | in | 1 | Saved direction prediction from fetch stage |
| `btb_hit` | in | 1 | Saved BTB hit status from fetch stage |
| `predicted_target` | in | 32 | Saved BTB target from fetch stage |
| `actual_taken` | in | 1 | True branch condition outcome from ALU |
| `actual_target` | in | 32 | True calculated branch target from ALU |
| `mispredict` | out | 1 | Misprediction indicator (direction or target) |
| `flush` | out | 1 | Invalidation strobe to squash wrong-path pipeline stages |
| `redirect` | out | 1 | Fetch redirection enable signal |
| `redirect_pc` | out | 32 | Corrected program counter for fetch redirection |

### `branch_prediction_unit` (Top-Level Subsystem Wrapper)

| Port Group | Ports | Width | Description |
|---|---|:-:|---|
| **Clock/Reset** | `clk`, `reset` | 1 | System clock and synchronous reset |
| **Fetch Interface** | `fetch_pc` | 32 | Current instruction address for lookup |
| | `predicted_taken` | 1 | Combined BHT direction prediction |
| | `prediction_state` | 2 | Current 2-bit counter state (`00`, `01`, `10`, `11`) |
| | `btb_hit` | 1 | BTB tag match status |
| | `predicted_target` | 32 | Cached target address |
| | `predicted_next_pc` | 32 | Speculative next PC |
| | `selected_next_pc` | 32 | Subsystem fetch PC (redirect priority over speculative) |
| **Resolution Interface** | `resolve_valid` | 1 | Execute stage branch validity |
| | `resolve_pc` | 32 | PC of resolving branch |
| | `resolve_predicted_taken` | 1 | Saved fetch direction |
| | `resolve_btb_hit` | 1 | Saved BTB hit status |
| | `resolve_predicted_target` | 32 | Saved predicted target |
| | `resolve_actual_taken` | 1 | Evaluated branch outcome |
| | `resolve_actual_target` | 32 | Evaluated branch target |
| | `mispredict` | 1 | Misprediction flag |
| | `flush` | 1 | Pipeline squash strobe |
| | `redirect` | 1 | Fetch redirection strobe |
| | `redirect_pc` | 32 | Corrected next PC |

---

## 7. Verification Summary & Test Results

| Testbench | Module Under Test | Checks | Result | Execution Command |
|---|---|:-:|:-:|---|
| `tb_branch_control.sv` | `next_pc_mux` + `branch_resolution` | 24 | ✅ 24/24 PASS | `make test-p3` |
| `tb_integrated.sv` | BHT + BTB + Next-PC + Resolution | 26 | ✅ 26/26 PASS | `make test-p3-integrated` |
| `tb_branch_prediction_unit.sv` | `branch_prediction_unit` (INDEX_BITS=4) | 70 | ✅ 70/70 PASS | `make test-bpu` |
| `tb_branch_prediction_unit.sv` | `branch_prediction_unit` (INDEX_BITS=5) | 70 | ✅ 70/70 PASS | `make test-bpu` |
| **Total Regression** | **All P3 & Integrated BPU Blocks** | **190** | **✅ 190/190 PASS** | `make verify-p3 && make test-bpu` |

---

## 8. Waveform Evidence & VCD Provenance

All simulation waveforms are digital waveform diagrams plotted directly from genuine Icarus Verilog VCD dumps using Python Matplotlib renderers under a simulated 10 ns testbench clock (not measured hardware Fmax):

| Waveform File | Source VCD & Provenance | Generating Script | Key Visual Verification Points |
|---|---|---|---|
| `evidence/waveforms/p1_bht.png` | `results/p1_bht.vcd` (`make test-p1`, timescale 1ps) | `scripts/render_p1_waveform.py` | **Independently captured evidence for Shubhaang's P1 RTL:** Verifies 2-bit counter state progression `01 → 10 → 11 → 10 → 01 → 00`, reset to `01`, saturation at `11` and `00`, and index isolation. |
| `evidence/waveforms/bpu_integration.png` | `results/bpu_integration.vcd` (`make test-bpu` pass 2, `INDEX_BITS=5`, timescale 1ps) | `scripts/render_bpu_waveform.py` | **Top-level BPU proof:** Shows cold fetch fallthrough, direction mispredict flush & redirect, correct taken+BTB-hit combinational next-PC selection (with no recovery redirect in this test case), target mispredict recovery, and redirect priority over speculative fetch. |
| `evidence/waveforms/p3_integrated_simulation.png` | `results/p3_integrated.vcd` (`make test-p3-integrated`, timescale 1ps) | `scripts/render_p3_waveform.py` | Closed-loop integration timing showing metadata sampling, redirect priority, and loop backward branch resolution. |
| `evidence/waveforms/p3_control.png` | Conceptual / RTL | Matplotlib | Architectural timing diagram showing fetch and resolution pipeline stages. |

> **Authorship Credit Note:**
> - Top-Level BPU Subsystem Wrapper (`branch_prediction_unit.v`) and PR #8: Shubhaang (@S-h-u-b-h-1)
> - P1 2-bit BHT RTL (`predictor_2bit.v`, `branch_history_table.v`): Shubhaang (@S-h-u-b-h-1)
> - P2 Tagged BTB RTL (`branch_target_buffer.v`): Tanish (@tanishrao13)
> - P3 Next-PC & Resolution RTL (`next_pc_mux.v`, `branch_resolution.v`), Integration Harness (`tb_integrated.sv`), and Python Waveform Renderers: Tanmay Singh (@tanmay-7706)

---

## 9. Generic Synthesis Results

Synthesized using Yosys generic cell mapping (`synth -flatten; check -assert`):
- `next_pc_mux`: 112 generic cells (27 AND, 32 MUX, 28 XOR/XNOR)
- `branch_resolution`: 214 generic cells (110 AND, 22 MUX, 55 XOR/XNOR/OR)
- `branch_prediction_unit`: 2,993 generic cells (combining all 4 subsystem blocks into a single top-level netlist)
- All synthesis checks pass with **0 latches, 0 combinatorial loops, and 0 assertion warnings**.

---

## 10. Scope and Architectural Boundaries

1. **Subsystem Scope:** The BPU wrapper handles branch prediction, target calculation, and fetch redirection. It does not replace full CPU pipeline registers (e.g., IF/ID, ID/EX).
2. **Flush Implementation:** In a full processor core, `flush` is connected to the synchronous clear / invalidate lines of younger pipeline registers.
3. **Single Branch in Flight:** The current test harness evaluates one resolving branch per clock cycle. Deeply superscalar speculative branch checkpointing is outside the scope of Phase I.
4. **Technology Independence:** Cell counts reflect generic technology-independent gates. FPGA LUT mapping and timing closure are evaluated in Phase II.

---

## 11. Files Authored & Maintained (P3)

- `rtl/next_pc_mux.v` — Speculative next-PC multiplexer
- `rtl/branch_resolution.v` — Misprediction detection and recovery logic
- `testbench/tb_branch_control.sv` — Unit testbench (24 checks)
- `testbench/tb_integrated.sv` — Integration testbench (26 checks)
- `scripts/render_p1_waveform.py` — P1 BHT waveform rendering script
- `scripts/render_bpu_waveform.py` — BPU integration waveform rendering script
- `scripts/render_p3_waveform.py` — P3 simulation waveform rendering script
- `video/P3_DEMO_SCRIPT.md` — Tanmay's video clip narration and screen recording guide
- `docs/P3_PIPELINE_CONTROL.md` — Architectural specification and design rationale
- `report/P3_REPORT_SECTION.md` — Section III-C and Section V IEEE project report contributions
