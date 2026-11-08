# P3 Prototype Video Script & Narration — Tanmay Singh

**Presenter:** Tanmay Singh
**Role:** Person 3 (P3) — Next-PC Selection, Branch Resolution, and Control Integration
**Recipient / Video Editor:** Vansh (@VanshP018)
**Target Segment Length:** 35 seconds total (0:10 member intro + 0:35 technical demonstration)
**Status:** Ready for recording / final audio & video track splice

---

## 1. Video Allocation & Storyboard Sync

In the 5-member Phase I demonstration video (`video/DEMO_STORYBOARD.md`), Tanmay delivers two segments:

1. **Member Introduction (0:30–0:40, 10s):** Name, role, and subsystem responsibility.
2. **Technical Demonstration (2:05–2:40, 35s):** Next-PC selection, execute-stage branch resolution, pipeline recovery redirection, and BPU integration proof.

---

## 2. Spoken Narration Script (Verbatim)

### Segment A: Self-Introduction (Timestamp: 0:30 – 0:40)
> *"Hi everyone, I am Tanmay Singh, responsible for Person 3: Next-PC Selection, Branch Resolution, and Control Integration for our Branch Prediction Unit."*

### Segment B: Technical Demonstration & Verification (Timestamp: 2:05 – 2:40)
*(Screen shows clean terminal running `make test-p3 test-p3-integrated && make test-bpu`, followed by waveform display of `evidence/waveforms/bpu_integration.png`)*

> *"I designed the control logic that interfaces our 2-bit BHT and tagged BTB to the processor pipeline.*
>
> *During fetch, the `next_pc_mux` speculatively steers execution: when the predictor indicates taken and the BTB hits, it branches immediately to the cached target; on a BTB miss or not-taken prediction, it safely falls back to sequential PC plus 4.*
>
> *During execution, `branch_resolution` evaluates the actual outcome against saved fetch metadata. Looking at our verified simulation waveform: on a direction misprediction or target mismatch, the unit asserts `mispredict`, pulses `flush` to squash wrong-path instructions, and asserts `redirect` to steer fetch to the corrected target.*
>
> *The recovery redirect has strict priority over speculative fetch. All 50 P3 unit tests and all 140 top-level BPU integration checks pass cleanly across parameter sizes."*

---

## 3. Visual Recording Instructions (For Screen Capture)

### Scene 1: Terminal Verification (Duration: ~15s)
- **Directory:** Repository root (`MCA/`)
- **Action:** Run the full P3 and BPU test suites:
  ```bash
  make test-p3 test-p3-integrated
  make test-bpu
  ```
- **Visual Cue:** Show all 24 branch control checks passing, all 26 integrated checks passing, and all 140 BPU regression checks (70 on `INDEX_BITS=4`, 70 on `INDEX_BITS=5`) with zero failures.

### Scene 2: Waveform Inspection (Duration: ~20s)
- **Asset Displayed:** Open `evidence/waveforms/bpu_integration.png` (or view `results/bpu_integration.vcd` in GTKWave/Surfer).
- **Cursor Focus Areas:**
  1. **Phase 1 (Cold Fetch, 25ns):** `predicted_taken=0`, `btb_hit=0`, `selected_next_pc=0x1004` (PC+4 fallback).
  2. **Phase 2 (Mispredict Recovery, 40ns):** `mispredict=1`, `flush=1`, `redirect=1`, `redirect_pc=0x2000`, `selected_next_pc` redirected to `0x2000`.
  3. **Phase 3 (Zero-Bubble Hit, 60ns):** `predicted_taken=1`, `btb_hit=1`, `predicted_target=0x2000`, `mispredict=0`, `flush=0` (seamless pipelined execution).
  4. **Phase 4 (Target Misprediction, 80ns):** Resolved target mismatch (`0x3000` vs `0x2000`), recovery `redirect_pc=0x3000`.
  5. **Phase 5 (Direction Misprediction T→NT, 100ns):** `redirect_pc=0x1004` (branch PC+4 recovery).

---

## 4. Deliverables Handoff to Vansh (@VanshP018)

| Artifact | Repository Path | Description |
|---|---|---|
| **P1 BHT Waveform** | `evidence/waveforms/p1_bht.png` | Genuine simulation waveform of Shubhaang's 2-bit BHT showing `01 → 10 → 11 → 10 → 01 → 00` state progression |
| **BPU Integration Waveform** | `evidence/waveforms/bpu_integration.png` | Genuine simulation waveform of `branch_prediction_unit.v` showing speculative fetch, mispredict recovery, and redirect priority |
| **P3 Simulation Waveform** | `evidence/waveforms/p3_integrated_simulation.png` | Detailed VCD simulation timing diagram from `tb_integrated.sv` |
| **P3 Control Waveform** | `evidence/waveforms/p3_control.png` | Architectural timing diagram of next-PC mux and resolution signals |
| **P3 Unit Log** | `evidence/control_logs/p3_control_test.log` | 24 passing assertions (`tb_branch_control.sv`) |
| **P3 Integration Log** | `evidence/control_logs/p3_integrated_test.log` | 26 passing checks (`tb_integrated.sv`) |
| **P3 Synthesis Log** | `evidence/control_logs/p3_synthesis_checked.log` | Yosys checked generic cell counts (112 cells `next_pc_mux`, 214 cells `branch_resolution`) |
| **BPU Test Logs** | `results/bpu_test_4.log`, `results/bpu_test_5.log` | 140 passing BPU integration checks (`tb_branch_prediction_unit.sv`) |

---

## 5. Speaker Checklist Before Video Submission
- [x] Spoken duration strictly within 35 seconds.
- [x] Clear pronunciation of technical terms (`next_pc_mux`, `branch_resolution`, `2-bit BHT`, `tagged BTB`, `flush`, `redirect`).
- [x] Terminal text and waveform signal labels are crisp and readable (1080p minimum).
- [x] Independent authorship boundaries respected: P1 (Shubhaang), P2 (Tanish), P3 (Tanmay), P4 (Vansh), P5 (Lakshya).
