# MCA Phase II — final live evaluation runbook

**Team:** master-slave (Section C) · **Project:** Dynamic Branch Prediction Unit (Project 5)
**Tuesday 24 November 2026, 1:45–2:00 PM IST, Room A410**. All five members must attend. Arrive before the slot; do not depend on extension time.

## What has actually been delivered

- Synthesizable P1 two-bit BHT, P2 tagged BTB, P3 next-PC/recovery, and combined `rtl/branch_prediction_unit.v` (not a full CPU).
- P4 always-not-taken/one-bit/two-bit comparisons on three deterministic synthetic traces; independent Verilog/Python reconciliation.
- P5 reproducible generic synthesis and illustrative CPI analysis; IEEE Phase I report; final 4:53.7 video and official Phase I Google Form receipt.
- **Phase II IEEE report:** `report/Phase2_Final_IEEE_Report.pdf` (built from the checked `.tex` source by the Phase II workflow). Corrected Tanish's surname against the official faculty team list; retained Lakshya's name as supplied, without guessing a surname.
- Existing module and integrated BPU tests are documented. Consult the latest successful GitHub Actions run before claiming the newest `main` passed.

## Fifteen-minute rehearsal schedule (adapt to faculty questions)

| Clock | Member | Show and explain |
|---|---|---|
| 0:00–1:15 | Shubhaang | Problem: 5-stage pipeline control hazard; what BPU predicts and project scope |
| 1:15–3:15 | Shubhaang | BHT: 16 two-bit counters, PC[5:2], 01 reset, 00/01 NT, 10/11 T, hysteresis, aliasing |
| 3:15–4:45 | Tanish | BTB: valid/tag/target, hit, tag collisions, taken-only training and PC+4 fallback |
| 4:45–6:45 | Tanmay | Saved fetch-time prediction metadata; next-PC mux, wrong direction/target, flush/redirect priority |
| 6:45–8:45 | Vansh | Three identical traces, independent Python oracle, 130 branches, two-bit strengths and alternating counterexample |
| 8:45–10:15 | Lakshya | Accuracy, model-only CPI, Yosys generic synthesis, Fmax limitation |
| 10:15–11:45 | Live demo | One or two self-checking commands, the committed waveform, table/graph |
| 11:45–15:00 | All | Faculty viva; leader coordinates, individual contributor answers their part |

Do not spend the entire slot playing the 4:53.7 Phase I video. Open it only if requested.

## One complete example everyone must know

At fetch PC `0x100`, BHT predicts Taken; BTB returns target `0x200` when tag/valid match, so speculative PC = `0x200`. An older branch might simultaneously resolve at an entirely different PC. The caller must preserve that older branch's **original prediction**; if it was wrong, P3 asserts `mispredict`, `flush`, `redirect`, and chooses its actual next PC. Only valid resolved branches train the BHT, and only valid Taken resolutions train the BTB.

### Counter progression: start 01, outcomes T,T,NT,NT
Predictions **before** each update: NT, T, T, T. Updated states: 10, 11, 10, 01. This is the exact four-state saturating table used in RTL.

## Verified, repeatable numbers (not modern CPU benchmarks)

| Workload | Dynamic branches | Always-NT correct | One-bit correct | Two-bit correct |
|---|---:|---:|---:|---:|
| Loop-like | 40 | 8 | 24 | 31 |
| Alternating | 40 | 20 | 0 | 0 |
| Mixed BEQ/BNE | 50 | 20 | 23 | 24 |
| **Overall** | **130** | **48 (36.92%)** | **47 (36.15%)** | **55 (42.31%)** |

On mixed BEQ/BNE, changing from a 16-entry to a 32-entry BHT improved two-bit correctness from 24/50 to 37/50, **only for this selected trace**. The 2-bit predictor is not universally superior: both dynamic predictors get 0/40 on strict alternation.

**Illustrative (not measured) CPI:** `CPI = 1 + 0.2 × misprediction_rate × 3`. Always NT 1.378462; one bit 1.383077; two bit 1.346154.

**Generic Yosys 0.33 cells:** BPU 2,993, BTB 2,498, two-bit predictor 162. These separately synthesized top counts must not be added. A different Yosys 0.70+post video run showed 2,907 generic BPU cells. **New device-specific estimate:** the unchanged BPU inside a registered I/O timing harness mapped to iCE40HX8K-CT256 achieved **93.22 MHz software-estimated post-route Fmax**, 427 LUT4s, 279 FFs, 56 carry cells and 4 RAM40 blocks; requested clock 25 MHz met. [Evidence](../evidence/fpga_timing/POSTROUTE_RESULT.md). Neither is physically measured board frequency.

## Demonstration commands

Run from the repository root (install `iverilog`, `yosys`, Python 3 and plotting dependencies in advance):

```bash
git rev-parse --short HEAD
make test-bpu                     # Integrated 16/32-entry BPU
make test-p1                      # Shubhaang's BHT basics
make test-btb                     # Tanish's BTB
make test-p3                      # Tanmay's branch control
make test-p4-compare              # Vansh HDL/Python parity
make metrics test-p5-metrics      # Lakshya's validated data
make synth-all                    # Seven generic Yosys tops
make waveforms                    # Real VCD-derived PNGs
```

For a quick viva run, start with `make test-bpu`, then show `evidence/waveforms/bpu_integration.png` and `evidence/metrics/accuracy.svg`. Keep the final PDF open as backup. `make test` is the comprehensive software regression, not the best first command during a strict 15-minute slot.

## High-probability cross-questions

- **Why predict?** Conditional branches introduce control hazards; prediction keeps fetch speculative while resolution is pending.
- **What is a BHT?** A PC-indexed table of direction history/counters; our default is 16 × two bits (32 counter bits).
- **Why 2-bit rather than 1-bit?** Hysteresis protects the direction prediction from one contrary result.
- **Why PC[5:2]?** The lower two bits are zero for aligned 4-byte instructions; four bits index 16 entries.
- **What is aliasing?** Two different PCs share one BHT counter; their training may interfere.
- **Why BTB tag?** A target lookup must check that its stored target belongs to the current branch PC.
- **What if predicted Taken but BTB missed?** Our speculative next PC falls back to PC+4; a valid actually Taken branch will redirect after resolution.
- **Why save prediction metadata?** Current live lookup may be unrelated to the older branch resolving now.
- **What is flush?** A request to discard younger wrong-path work; a full CPU would implement detailed stage kills outside this BPU.
- **What was tested?** Directed self-checking SystemVerilog for counter, target, recovery and integrated wrapper, plus an independent Python model.
- **Why is CPI not measured?** No full CPU program execution; branch fraction and penalty are assumed.
- **What is Fmax?** Highest supported clock under a device-specific implementation/timing model. Our **registered BPU wrapper's software post-route estimate is 93.22 MHz** on iCE40HX8K-CT256. Actual physical board Fmax remains unmeasured.
- **How improve?** Real five-stage integration, actual instruction traces, gshare, mapped FPGA timing and power/area analysis.

## Before 24 November — responsible signoffs

- [ ] Shubhaang: run latest complete `main` CI/tests, review the Phase II report and rehearse opening/cross-questions.
- [ ] Tanish: verify surname as on official evaluation notice, demonstrate BTB hit/tag collision; explain the 93.22 MHz **software routing estimate** and why physical Fmax is still unmeasured.
- [ ] Tanmay: rehearse one direction error and one wrong-target recovery from saved metadata.
- [ ] Vansh: demonstrate source counts, show the 2-bit counterexample (alternating 0/40), and confirm final five-member video ownership.
- [ ] Lakshya: verify all five displayed author details and Phase II final report, explain Yosys tool-version difference and model-only CPI.
- [ ] All: inspect the final PDF, verify it reflects genuine contributions, review the original video (browser playback), and bring laptops/chargers/offline PDF/evidence. Obtain faculty guidance if target-specific FPGA Fmax is demanded.

**Scope statement to use if pressed:** “We implemented and verified a synthesizable branch-prediction subsystem and its recovery interface, not a complete pipelined CPU. Our predictor accuracy is measured on deterministic synthetic traces. CPU speedup and maximum FPGA frequency are not measured.”
