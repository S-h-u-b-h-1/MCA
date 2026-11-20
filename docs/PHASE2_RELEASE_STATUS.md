# MCA Project 5 — Phase II Engineering Release Status

**Engineering verification date:** 20 November 2026  
**Evaluation:** Tuesday 24 November 2026, **1:45–2:00 PM IST**, **A410**  
**Team:** `master-slave`, Section C; Shubhaang Kataruka, Tanish Yadav, Tanmay Singh, Vansh Panwar and Lakshya.

## 1. Deliverables prepared and verified

| Item | Status | Evidence |
| --- | --- | --- |
| P1 two-bit BHT | Passed | [Main P1 regression](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125331) |
| P2 tagged BTB | Passed | [Main BTB verification](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125215) |
| P3 next-PC / recovery | Passed | [Main P3 verification](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125233) |
| P4 baseline/trace comparisons | Passed | [Main P4 verification](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125292) |
| P5 metrics and generic synthesis | Passed | [Metrics](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125225), [generic synthesis](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125256) |
| BPU 16/32-entry integrated checks | Passed | [Main integrated regression](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125241) |
| Technology-mapped FPGA timing | Passed; software estimate | [Main iCE40 routing run](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125409), [pinned result](../evidence/fpga_timing/POSTROUTE_RESULT.md) |
| Final IEEE report / full verification | Passed; PDF published | [Main report build](https://github.com/S-h-u-b-h-1/MCA/actions/runs/44781125288), [PDF](../report/Phase2_Final_IEEE_Report.pdf) |
| Phase I IEEE report and team video | Submitted | [Phase I PDF](../report/Phase1_IEEE_Report.pdf), [video](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing) |

**Verification:** All **nine named main-branch workflows** for the Phase II integration commit `dfb9c460129cb598c1a1c6d765c801c1537c6b1d` completed successfully. GitHub Actions then compiled and published the final IEEE PDF to main at commit `30a90e6594decc5436392a97b474758ff90c2b67`. The report was independently opened and rendered (3 pages, A4, IEEE two-column layout). The original Phase I PDF was preserved.

## 2. Quantitative facts for viva

- Predictor accuracy on **130 synthetic branch outcomes**: always-NT **48/130 (36.92%)**, one-bit **47/130 (36.15%)**, two-bit **55/130 (42.31%)**; loop-like two-bit **31/40 (77.50%)**; alternating dynamic predictors **0/40**.
- CPI values are **illustrative model outputs**, not measured CPU CPI. Assumptions: ideal CPI = 1, branch fraction = 0.2 and branch penalty = 3 cycles.
- Earlier Yosys 0.33 integration synthesis: **2,993 generic cells** (raw BPU top, not FPGA LUTs).
- New *technology-mapped, software post-route* registered-harness iCE40HX8K-CT256: **estimated Fmax 93.22 MHz**, **10.73 ns**, requested **25 MHz goal passed**; **427 LUT4**, **279 FF**, **56 carry**, **4 RAM40**. The preserved critical path passes from BTB tag storage through hit/next-PC selection to a capture register.
- Neither the model-based CPI nor the software Fmax result measures a physical CPU/FPGA board.

## 3. How to present in a 15-minute viva

1. Open [final Phase II IEEE report](../report/Phase2_Final_IEEE_Report.pdf) and [member-by-member viva runbook](PHASE2_LIVE_VIVA_RUNBOOK.md).
2. Explain the control hazard; BHT/BTB prediction at fetch; saved prediction metadata; actual branch resolution; flush/redirect.
3. Run `make test-bpu` if permitted, then show the [integrated waveform](../evidence/waveforms/bpu_integration.png), [accuracy comparison](../evidence/metrics/accuracy.svg) and [FPGA timing evidence](../evidence/fpga_timing/POSTROUTE_RESULT.md).
4. Have each member explain their own RTL/tests/metrics. Do not spend the full slot playing the Phase I video.
5. If faculty asks whether the project implements a complete CPU or achieved a measured 93.22 MHz on a board, answer **no**. This is a synthesizable BPU and a reported *software post-route estimate*.

## 4. External signoffs / remaining administration

Engineering verification is finished; **course/evaluation acceptance is not claimed**.

- **MCA course instructor / assigned evaluator:** confirm in writing whether the chosen board-less iCE40 device, registered test wrapper and external timing assumptions satisfy the course's Fmax requirement; otherwise request a specified actual FPGA target and constraints.
- **All five coauthors:** confirm final names, report contribution summaries, and any personal/consent requirements.
- **Team / faculty:** verify full anonymous playback of the submitted Phase I video. Automated anonymous playback produced a transient Drive error, although the original MP4 decoded successfully; do not claim uninterrupted streaming independently verified.
- **Live evaluation on 24 November:** still outstanding and must be attended in person by all five members.

Historical GitHub issue tracking: [#10](https://github.com/S-h-u-b-h-1/MCA/issues/10), [#11](https://github.com/S-h-u-b-h-1/MCA/issues/11), and [#12](https://github.com/S-h-u-b-h-1/MCA/issues/12).

**Authoritative source:** `report/Phase2_Final_IEEE_Report.tex` is the active editable IEEEtran source. The older `.tex.gz.b64` is retained only as legacy Phase II build input from the earlier release; new builds compile the readable `.tex` file directly.
