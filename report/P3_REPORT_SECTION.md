# P3 IEEE Report Contribution — Tanmay

**Section:** III. Proposed Solution — Subsection C: Next-PC Selection and Pipeline Recovery  
**Section:** V. Individual Contributions — Tanmay (P3)  
**Author:** Tanmay Singh (Person 3: Next-PC Selection, Branch Resolution, and Control Integration)
**Date:** 8 November 2026 (Updated for BPU Release Signoff & Issue #9)

---

## Section III-C: Next-PC Selection and Pipeline Recovery

### 1. Speculative Fetch-Stage Next-PC Selection
In a pipelined processor, instruction fetch cannot stall until branch condition evaluation without incurring severe throughput penalties. The Branch Prediction Unit must supply a speculative next program counter ($PC_{next}$) in the same cycle the current instruction address ($PC$) is presented.

The combinational `next_pc_mux` module evaluates the direction prediction from the 2-bit BHT ($P_{taken} \in \{0, 1\}$) and the Branch Target Buffer status ($BTB_{hit} \in \{0, 1\}$) to select between sequential fetch and speculative target redirection:

$$PC_{pred\_next} = \begin{cases} Target_{BTB}, & \text{if } P_{taken} = 1 \land BTB_{hit} = 1 \\ PC + 4, & \text{otherwise} \end{cases}$$

When the predictor indicates a branch is taken but the BTB experiences a capacity or conflict miss ($BTB_{hit} = 0$), the hardware conservatively defaults to the sequential path ($PC + 4$). The correct target is subsequently resolved and recovered in the execution stage.

### 2. Execute-Stage Branch Resolution and Recovery
During branch execution, the architectural branch condition ($A_{taken} \in \{0, 1\}$) and calculated target address ($Target_{actual}$) are resolved. Crucially, the resolution logic does not query current predictor states; rather, it evaluates against the *saved fetch-time prediction metadata* ($P_{taken}, BTB_{hit}, Target_{pred}$) captured in pipeline registers at fetch time.

A misprediction signal is asserted whenever:
1. The predicted direction differs from the architectural outcome ($P_{taken} \neq A_{taken}$).
2. The branch was taken ($A_{taken} = 1$), but either the BTB missed ($BTB_{hit} = 0$) or the predicted target did not match the resolved target ($Target_{pred} \neq Target_{actual}$).

Formally, the recovery condition is:

$$\text{Mispredict} = \text{Valid} \land \Big( (P_{taken} \neq A_{taken}) \lor \big( A_{taken} \land (\neg BTB_{hit} \lor (Target_{pred} \neq Target_{actual})) \big) \Big)$$

When $\text{Mispredict} = 1$, the module asserts:
- $\text{Flush} = 1$: Invalidation signal for younger wrong-path instructions.
- $\text{Redirect} = 1$: Control signal steering the fetch unit to the corrected architectural PC.
- $\text{Redirect\_PC} = A_{taken} \; ? \; Target_{actual} : (PC_{branch} + 4)$.

### 3. Subsystem Scope: Synthesizable BPU vs. CPU Pipeline Boundaries
The synthesizable top-level module `branch_prediction_unit.v` integrates P1 (2-bit BHT), P2 (tagged BTB), and P3 (`next_pc_mux`, `branch_resolution`) into a unified hardware block. In this integrated unit:
- The fetch stage combinational path generates $PC_{pred\_next}$.
- A top-level selection multiplexer enforces strict architectural priority:

$$PC_{fetch\_selected} = \text{Redirect} \; ? \; \text{Redirect\_PC} : PC_{pred\_next}$$

> **Architectural Boundary Note:** The prototype synthesizes and verifies the complete **Branch Prediction Subsystem and recovery interface**. Surrounding CPU execution units—such as physical inter-stage pipeline registers (IF/ID, ID/EX, EX/MEM, MEM/WB), instruction and data memories, register files, and ALU condition comparators—are deliberately outside the BPU subsystem boundary and are modeled by the verification testbenches (`tb_integrated.sv`, `tb_branch_prediction_unit.sv`).

### 4. Hardware Complexity and Generic Synthesis
The P3 control blocks and integrated BPU subsystem synthesize cleanly with zero assertion warnings under Yosys generic cell synthesis:
- `next_pc_mux`: 112 generic cells (27 AND, 32 MUX, 28 XOR/XNOR) with zero sequential overhead.
- `branch_resolution`: 214 generic cells (110 AND, 22 MUX, 55 XOR/XNOR/OR).
- `branch_prediction_unit`: 2,993 generic cells after flattening, encapsulating all tables, multiplexers, and recovery logic (see `evidence/synthesis/summary.md`).

---

## Section V: Individual Contributions — Tanmay Singh (P3)

**Tanmay Singh (P3)** designed, implemented, and verified the pipeline control and recovery interface for the Branch Prediction Unit:

- **RTL Architecture:** Authored synthesizable Verilog modules `rtl/next_pc_mux.v` (speculative fetch multiplexer) and `rtl/branch_resolution.v` (execute-stage comparison and flush/redirect generation). Integrated these blocks into the project's verified top-level subsystem `rtl/branch_prediction_unit.v`.
- **Unit Verification:** Developed `testbench/tb_branch_control.sv` containing 24 directed assertions verifying all combinations of the branch control truth table, edge cases (PC=0, boundary wrap-around, zero targets), and back-to-back alternations (24/24 PASS).
- **Subsystem Integration & Authorship Credit:**
  - Integrated P3 control logic into the synthesizable top-level subsystem `rtl/branch_prediction_unit.v` (authored by Shubhaang, `@S-h-u-b-h-1`, PR #8).
  - Authored closed-loop integration harness `testbench/tb_integrated.sv`, verifying P1 BHT (Shubhaang), P2 BTB (Tanish), and P3 Control in a realistic fetch-predict-resolve cycle with metadata preservation (26/26 PASS).
- **Top-Level BPU Regression:** Co-verified `testbench/tb_branch_prediction_unit.sv` across parameterized table sizes (`INDEX_BITS=4` and `INDEX_BITS=5`), achieving 140/140 passing assertions under `make test-bpu`.
- **Waveform Evidence Generation & Provenance:**
  - Authored `scripts/render_p1_waveform.py` and captured `evidence/waveforms/p1_bht.png` from `results/p1_bht.vcd`, providing independently captured verification evidence for Shubhaang's P1 2-bit BHT RTL (`01 → 10 → 11 → 10 → 01 → 00` state progression, reset, saturation, and indexing) without claiming RTL authorship.
  - Authored `scripts/render_bpu_waveform.py` and captured `evidence/waveforms/bpu_integration.png` from `results/bpu_integration.vcd` (pass 2 of `make test-bpu`, `INDEX_BITS=5`, 32 BHT entries, 32 BTB sets), demonstrating cold-start fallback, direction mispredict flush and redirect, correct taken+BTB-hit combinational next-PC selection (with no recovery redirect in this test case), target mispredict recovery, and redirect priority.
  - Authored `scripts/render_p3_waveform.py` and generated `evidence/waveforms/p3_integrated_simulation.png` from `results/p3_integrated.vcd`.
  - All waveform figures are digital waveform diagrams plotted directly from verified VCD dumps with Matplotlib and evaluated under simulated 10 ns testbench clock stimulus (not measured hardware Fmax).
- **Tool Automation & Makefile:** Extended `Makefile` with `test-p3`, `test-p3-integrated`, `synth-p3-checked`, `waveform-p1`, `waveform-p3`, `waveform-bpu`, `waveforms`, and `verify-p3` with strict nonzero exit checks.
- **Documentation & Demo Script:** Authored comprehensive architectural specification `docs/P3_PIPELINE_CONTROL.md` and prepared the narrated video demonstration script `video/P3_DEMO_SCRIPT.md` for compilation into the Phase I prototype video by Vansh (`@VanshP018`).
