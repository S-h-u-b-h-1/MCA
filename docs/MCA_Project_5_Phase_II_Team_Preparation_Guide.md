# MCA Project 5 — Phase II Team Preparation Guide

**Dynamic Branch Prediction Unit** · Team **master-slave** · Section **C**  
**Evaluation:** Tuesday **24 November 2026**, **1:45–2:00 PM IST**, **Room A410**  
**Team:** Shubhaang Kataruka (P1/lead), Tanish Yadav (P2), Tanmay Singh (P3), Vansh Panwar (P4), Lakshya (P5)

> This is the web-readable companion to the 13-page PDF/Word preparation guide, distributed in the team's 20 November 2026 viva pack. The [detailed live runbook](PHASE2_LIVE_VIVA_RUNBOOK.md) is the authoritative demo schedule. Engineering evidence is frozen for the viva, but faculty approval of the timing method is not yet recorded.

## 1. What we built, in plain language

A branch such as BEQ/BNE introduces a **control hazard** in a pipeline because fetch needs the next PC before the condition is resolved. Our **synthesizable prediction subsystem**, not a full CPU, has three major elements:

1. **BHT** (Shubhaang): predicts **Taken/Not Taken** using 16 indexed 2-bit saturating counters. Reset state is `01`; `PC[5:2]` indexes 16 entries; the MSB is the prediction. `00/01` predict Not Taken and `10/11` Taken. Branches at `0x100` and `0x140` alias into the same tagless BHT entry.
2. **Tagged BTB** (Tanish): predicts **target address** when it has a valid/tag-matching entry. Each entry has valid, tag and target fields. A colliding tag replaces the old target. Only valid **actually Taken** branch resolutions train it.
3. **Next-PC/recovery** (Tanmay): if `predicted_taken && btb_hit`, select the BTB target; otherwise select `PC+4`. A resolving branch is compared with its **saved original fetch-time prediction**, not a new live lookup. Wrong direction or wrong target triggers `mispredict`, `flush`, `redirect` and `redirect_pc`. Redirect overrides simultaneous speculation.

### BHT state transitions

| State | Prediction | Actual Taken -> new state | Actual Not Taken -> new state |
|---|---|---|---|
| `00` strong NT | NT | `01` | `00` |
| `01` weak NT | NT | `10` | `00` |
| `10` weak T | T | `11` | `01` |
| `11` strong T | T | `11` | `10` |

For outcomes `T, T, NT, NT` starting from `01`: **predictions before updates** are `NT, T, T, T`; **states after updates** are `10, 11, 10, 01`.

## 2. Individual viva ownership

| Member | Files / what to demonstrate | Must be able to explain |
|---|---|---|
| **Shubhaang** | `rtl/branch_history_table.v`, `rtl/predictor_2bit.v` | Saturating counter, reset priority, why `PC[5:2]`, tagless aliasing, simultaneous fetch and update |
| **Tanish** | `rtl/branch_target_buffer.v`, `testbench/tb_btb.sv` | Valid/tag/target, cold miss, hit, collision/replacement, taken-only training |
| **Tanmay** | `rtl/next_pc_mux.v`, `rtl/branch_resolution.v`, BPU wrapper | Saved prediction metadata, actual-next-PC, target miss, wrong-target recovery and flush/redirect |
| **Vansh** | `rtl/predictor_1bit.v`, `testbench/tb_comparison.sv`, Python oracle | Fair trace comparison, predict-before-train, loop hysteresis, alternating counterexample, aliasing |
| **Lakshya** | `scripts/synth_all.sh`, `scripts/collect_metrics.py`, IEEE report | Accuracy/CPI formulas, mapped versus generic cells, FPGA timing evidence, precise limitations |

## 3. Numeric results — do not memorize unsupported claims

All three methods received **the same deterministic synthetic 130-branch stream**; this is **not** a real CPU benchmark.

| Workload | Branches | Always NT correct | One-bit correct | Two-bit correct |
|---|---:|---:|---:|---:|
| Loop-like | 40 | 8 | 24 | 31 |
| Alternating | 40 | 20 | 0 | 0 |
| Mixed BEQ/BNE | 50 | 20 | 23 | 24 |
| **Overall** | **130** | **48 (36.92%)** | **47 (36.15%)** | **55 (42.31%)** |

The 2-bit BHT does **not** always win: strict alternation gives both dynamic predictors **0/40**. In this specific mixed trace, increasing BHT capacity from 16 to 32 entries improves 2-bit correct predictions from **24/50 to 37/50** by reducing aliasing.

Illustrative (not measured CPU) CPI: `CPI = 1 + 0.2 × direction_miss_rate × 3`. Two-bit = **1.346154**; always NT = **1.378462**; one-bit = **1.383077**. The ideal CPI, branch fraction and misprediction penalty are assumed.

## 4. FPGA mapping / Fmax — exact interview wording

We used **Yosys 0.33 synth_ice40** and **nextpnr-ice40 0.6** for a **registered I/O harness around the unchanged BPU**, targeting **Lattice iCE40HX8K-CT256**. A **25 MHz clock goal passed**; reported **software-estimated post-route Fmax was 93.22 MHz** (10.73 ns). Mapped resources: **427 LUT4s, 279 flip-flops, 56 carry primitives, four RAM blocks**. The critical path passes from **BTB tag RAM through the hit/next-PC selection to a registered observation output**.

**What this does not prove:** no actual FPGA board was programmed, physical frequency was **not** measured, no board PCF/pinout or full external timing constraints were supplied, and there is no full CPU. Our previous **2,993 Yosys generic cells** are a different unit/flow from these mapped FPGA primitives. The MCA instructor still needs to accept the virtual-board timing method.

Sources: [FPGA study](FPGA_TIMING_STUDY.md) · [raw timing evidence summary](../evidence/fpga_timing/POSTROUTE_RESULT.md) · [verified main timing run](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125409).

## 5. Fast demonstration and 15-minute use

**Run from the repository root after checking tool availability:**

```bash
git rev-parse --short HEAD
make test-bpu
make test-p1
make test-btb
make test-p3
make test-p4-compare
make metrics test-p5-metrics
make synth-all
# Pre-run on the laptop if nextpnr is installed:
bash scripts/run_fpga_timing.sh
```

Do **not** spend the entire strict 15-minute faculty slot running every command or streaming the 4:54 video. For live proof, **run `make test-bpu`**, then show `evidence/waveforms/bpu_integration.png`, `evidence/metrics/accuracy.svg` and the FPGA timing evidence summary. Have original verified logs and offline copies prepared.

Suggested order: 0:00–2:15 opening + BHT (Shubhaang); 2:15–3:45 BTB (Tanish); 3:45–5:45 next-PC/recovery (Tanmay); 5:45–7:45 baselines (Vansh); 7:45–9:30 metrics/Fmax (Lakshya); 9:30–11:30 short demo; remaining time cross-questions. Follow faculty interruptions.

## 6. Difficult questions everyone should answer

- **Why two PC inputs?** A new branch is being fetched while an older branch resolves; the PCs differ.
- **Why reset BHT to `01`?** Documented weakly-not-taken cold start, with reset priority on a rising clock edge.
- **Why does BHT not need BTB's tag?** BHT is intentionally tagless direction history; BTB must validate that a target belongs to the current PC.
- **When is training allowed?** Only `resolve_valid` branches train BHT; only valid actually Taken ones train BTB.
- **Why save fetch-time predictions?** The live lookup may already represent a different instruction.
- **Can we claim CPU speedup?** No: only synthetic branch trace accuracy and a parameterized CPI model were evaluated.
- **Is the Fmax physically measured?** No: **93.22 MHz is a routed-software estimate for an iCE40 registered BPU harness**.
- **Why doesn't 2-bit get 100%?** Cold-start effects, limited history, index aliasing, adversarial alternation, and nonstationary outcomes.

## 7. Final check before A410

Confirm all five attendees, verified names, final IEEE report PDF, real source revision, charged laptop and adapter, no network dependence, short demo, and a practiced explanation of both **what was implemented** and **what was not measured**. Coauthor consent/approval and MCA faculty signoff of the FPGA method are external and must not be assumed.

**Final report:** [Phase II IEEE PDF](../report/Phase2_Final_IEEE_Report.pdf) · [release status](PHASE2_RELEASE_STATUS.md) · [detailed viva runbook](PHASE2_LIVE_VIVA_RUNBOOK.md).
