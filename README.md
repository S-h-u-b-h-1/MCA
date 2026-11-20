# MCA — Dynamic Branch Prediction Unit (Project 5)

- **Team:** Shubhaang (leader/P1), Tanish (P2), Tanmay (P3), Vansh (P4), Lakshya (P5).
- **Phase I:** IEEE report, [4:53.7 team video](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing), and official Google Form submitted on 16 November 2026.
- **Phase II evaluation:** Tuesday **24 November 2026**, **1:45–2:00 PM IST**, **Room A410**, team `master-slave`, Section C. **All five members must attend.**
- **Phase II final deliverables:** [IEEE report (PDF)](report/Phase2_Final_IEEE_Report.pdf), [editable LaTeX source](report/Phase2_Final_IEEE_Report.tex), [live viva runbook](docs/PHASE2_LIVE_VIVA_RUNBOOK.md) and [final engineering release status](docs/PHASE2_RELEASE_STATUS.md).
- **Team preparation materials:** [Phase II team preparation guide](docs/MCA_Project_5_Phase_II_Team_Preparation_Guide.md), [one-page viva cheat sheet](docs/MCA_Project_5_Phase_II_One_Page_Viva_Cheat_Sheet.md) and [offline viva pack index](docs/MCA_Project_5_Phase_II_Offline_Viva_Pack_README.md). Formatted PDF/DOCX and offline ZIP are distributed separately.
- **Mapped FPGA timing:** [Lattice iCE40HX8K-CT256 software post-route study](evidence/fpga_timing/POSTROUTE_RESULT.md) estimates **93.22 MHz** for a registered wrapper around the verified BPU (25 MHz goal passed), with **427 LUT4s, 279 FFs, 56 carry cells and 4 RAM blocks**. **This is not a physical-board measurement.**
- **Scope and qualification:** Verified synthesizable *branch-prediction subsystem*, not a complete CPU. A physical board/pinout timing study and written MCA faculty acceptance of this virtual FPGA method remain pending.

## Scope

This is a **Verilog branch predictor prototype** with a 2-bit Branch History Table, 1-bit and static baselines, implemented tagged Branch Target Buffer, next-PC and branch-resolution control, and a trace-driven simulation harness. **It is not a complete pipelined CPU.**

## Verified starting point (22 Oct shared Mac log)

- `make test-p1`: 22/22 directed checks passed.
- `make synth-p1`: generic Yosys synthesis succeeded; 192 generic cells in the reported hierarchy, 0 check problems.
- `make demo`: one synthetic 32-branch trace; correct predictions 10 (always NT), 12 (1-bit), 15 (2-bit).
- `make test-p1-extended`: 184/184 checks passed on 3 November 2026.
- `make test-p1-scoreboard`: 8,443 + 9,163 + 10,123 checks passed across 4-, 16-, and 32-entry configurations.
- `make synth-p1-checked`: generic synthesis and design checks passed.
- `make test-btb`: P2 tagged BTB unit and parameter sweeps verified (merged in PR #2).
- `make test-p3`: 24/24 directed checks passed for next-PC mux and branch resolution (merged in PR #3).
- `make test-p3-integrated`: 26/26 integration checks passed for P1 BHT + P2 BTB + P3 control pipeline harness.
- `make verify-p3`: simulation (50/50 checks) and generic Yosys synthesis passed (0 errors; next_pc_mux 91 cells, branch_resolution 223 cells).
- `make check-traces`: validates schemas, monotonic sequence numbers, and operand conditions on committed traces.
- `make test-p4-unit`: 113/113 checks passed for expanded predictor assertion harness (cold start on 4 representative entries, 32-branch benchmark, reset priority, aliasing).
- `make test-p4-comparison`: 541/541 checks passed across 3 deterministic trace workloads (130 dynamic branches), P3 recovery coordination, and 16 vs 32-entry capacity sensitivity (48% vs 74%).
- `make test-p4-oracle`: independent Python reference model verifies 100% agreement with explicit benchmark regression assertions.
- `make test-p4-compare`: automated reconciliation script guarantees Verilog simulation and Python oracle parity across all counts and fields before publishing evidence.
- `make verify-p4`: full P4 simulation suite (654 checks), Yosys checked synthesis (0 problems, 92 cells for 1-bit, 284 cells for top), and dynamic VCD waveform generation completed.
- P5 synthesis automation, validated metrics and report/video handoff merged in PRs #5–#7; six workflows passed on combined main commit `97c8290`.
- Final QA PR #8 merged a synthesizable P1/P2/P3 wrapper and self-checking 16/32-entry integration regression (140/140 checks [passed in CI](https://github.com/S-h-u-b-h-1/MCA/actions/runs/42200408998)). The Phase I IEEE report is committed, and the final 293.7-second team demonstration is [hosted on Google Drive](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing).

## Mac setup

Install Icarus Verilog, Yosys and Surfer (Homebrew). In the project root:

```bash
make test-p1
make test-p1-extended
make test-p1-scoreboard
make verify-p1
make test-btb
make test-p3
make test-p3-integrated
make verify-p3
make check-traces
make test-p4-unit
make test-p4-comparison
make test-p4-oracle
make test-p4-compare
make verify-p4
make test-bpu
make test
make demo
make synth-p1
make synth-all
make metrics test-p5-metrics
surfer results/p1_bht.vcd
```

Generated outputs in `results/` are ignored by Git. Capture selected verified artefacts under `evidence/` for report/video.

## Working guides and roles

Read `docs/INTERFACES.md` first, then `docs/PROJECT_PLAN.md`, then your own guide in `docs/team_roles/`. Make authentic contributions through a personal Git branch and PR.

| Person | Role | New work required |
|---|---|---|
| Shubhaang | P1: BHT and 2-bit prediction | Strengthen verification, document state/indexing, review integration (Merged PR #1) |
| Tanish | P2: tagged BTB | Implement valid/tag/target cache + tests (Merged PR #2) |
| Tanmay | P3: next-PC + resolution | Implement next-PC, mispredict/flush/redirect and integrated harness (Merged PR #3) |
| Vansh | P4: baseline and verification | Extend 1-bit baseline; BEQ/BNE traces + independent comparison suite (Merged PR #4) |
| Lakshya | P5: synthesis, metrics and video | Automated synthesis + result analysis + final evidence and report assembly |

## Submission

- Use the [official IEEE conference templates](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/) unless faculty provides a specific local variant.
- **Final Phase I IEEE report:** [`report/Phase1_IEEE_Report.pdf`](report/Phase1_IEEE_Report.pdf) (approved for coursework submission by the team lead).
- **Final Phase I video:** [MCA team demonstration — 4 minutes 53.7 seconds](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing). The Google Drive file is shared **Anyone with the link → Viewer**; do not commit the MP4 to Git.
- [Demo access and media verification notes](video/DEMO_LINK.md).
- Confirm every team member appears in the video and has substantive commits and a report contribution.
- Submission form: https://docs.google.com/forms/d/e/1FAIpQLSc6Cx8OrOQLGj_X2ZMkyG5jc8mokq36mGRq2x8jGRNV1sbegA/viewform

## P1 independent verification handoff (3 Nov 2026)

See [P1 quickstart](docs/P1_QUICKSTART.md) and
[P1 implementation/viva notes](docs/P1_IMPLEMENTATION_NOTES.md).
The additional reference scoreboard tests `INDEX_BITS=2`, `4`, and `5`,
including all 8 direction/state transitions per entry, randomized updates,
reset priority, aliasing and concurrent lookup/update PCs.
The two existing P1 RTL files were intentionally **left unchanged** from the
22-check Mac-tested starting point. Extended tests and independent scoreboards **passed on Mac on 3 November 2026**.

## Faculty alignment and team onboarding

- [Faculty Project 5 and Phase I/II checklist](docs/FACULTY_REQUIREMENTS.md): completed evidence versus outstanding deliverables.
- [Start here for all teammates](docs/TEAM_START_HERE.md): forking, cloning, assigned branches and integration requirements; no collaborator invitation required.
- P1–P5, BPU QA (#8), BTB evidence (#13), P1/P3/BPU waveform evidence (#14), and IEEE report (#15) are merged. This is a branch-prediction prototype, not a full CPU. Target-specific Fmax remains unmeasured. The final video is linked above, and the Phase I form submission receipt was received on 16 November 2026.

## P5 evaluation and submission handoff

P5 contributions have been merged:
[synthesis #5](https://github.com/S-h-u-b-h-1/MCA/pull/5),
[metrics #6](https://github.com/S-h-u-b-h-1/MCA/pull/6), and
[report/video handoff #7](https://github.com/S-h-u-b-h-1/MCA/pull/7).

Final local validation on merged `main`:

```bash
make test
make synth-all
make metrics test-p5-metrics
```

- Generic synthesis: [seven-top evidence](evidence/synthesis/summary.md) from [successful Yosys 0.33 CI](https://github.com/S-h-u-b-h-1/MCA/actions/runs/42200408851); raw logs/netlists and tool/source-hash manifest are available from the CI artifact. Counts are generic, not FPGA LUTs or MHz.
- **Video versus pinned synthesis evidence:** the P5 capture shows 2,907 generic BPU cells under local Yosys 0.70+post; the committed Yosys 0.33 CI evidence reports 2,993 generic cells. Tool-version outputs are not directly comparable (see [demo verification notes](video/DEMO_LINK.md)).
- Accuracy/CPI: `evidence/metrics/accuracy.csv`, `accuracy.svg`, and `cpi_assumptions.md`.
- [P5 report contribution](report/P5_REPORT_SECTION.md) and [author handoff](report/PHASE1_REPORT_OUTLINE.md).
- [Video capture plan](video/DEMO_STORYBOARD.md), [submission checklist](docs/P5_SUBMISSION_CHECKLIST.md), and [BPU integration signoff](docs/BPU_RELEASE_SIGNOFF.md).

The [Phase I IEEE report](report/Phase1_IEEE_Report.pdf) is committed. The [final team demonstration](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing) is 4:53.7 (measured using `ffprobe`) and is also linked from [`video/DEMO_LINK.md`](video/DEMO_LINK.md). The form is submitted. Formal five-author acknowledgments and a faculty timing/Fmax decision are separate evidence gates, not claimed as complete here.
