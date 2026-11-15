# Faculty requirements and evidence gates — MCA Project 5

**Source:** [Modern Computer Architecture Project 5](https://docs.google.com/document/d/1CoQOY3T4p0qY1B9qR3WPh8I93aCyN-zIs9VF17kBMNU/edit).
Phase I deadline: **16 November 2026, 11:59 PM IST**.

## Current implementation

P1–P5 contributions (PRs #1–#7), integrated BPU QA (#8), BTB/waveform evidence
(#13 and #14), and the Phase I IEEE PDF (#15) are merged. This is a
branch-direction/target prediction **prototype**, not a complete pipelined CPU.
The last documented complete main CI workflow suite was successful at `ee7f45c`
(7 November); a new full CI result on the later report/submission commits is not claimed.

| Faculty objective | Evidence | Remaining |
| --- | --- | --- |
| 2-bit BHT, baseline 1-bit/static predictors | P1/P4 RTL, self-checking unit and independent scoreboards | None for module-level scope |
| Tagged BTB | P2 RTL, directed and parameterized tests | BTB logs, waveform and author-approved report section merged (#13); demo hosted |
| Next PC, mispredict/flush/redirect | P3 modules and interface-level integration; proposed synthesized BPU wrapper | Integrated wrapper merged (#8); 140/140 directed BPU CI checks |
| BEQ/BNE loop-oriented traces | 130 synthetic branches with HDL/Python parity | Disclose deterministic trace and cold-start limits |
| Accuracy/CPI | `evidence/metrics/accuracy.csv`, `accuracy.svg`, `cpi_assumptions.md` | CPI is illustrative, not CPU-measured |
| Logic resources | Seven-top Yosys 0.33 generic synthesis completed on the QA branch; manifest/netlists verified | Seven-top generic Yosys synthesis documented; no FPGA LUTs or Fmax claimed |
| Maximum frequency | No selected FPGA, constraints or post-route timing report | **Unmeasured**; agree valid target flow or faculty-approved limitation |
| IEEE technical report | P3/P4/P5 draft sections, P1/P2 design notes | Final PDF committed by PR #15; five-author acknowledgment set not independently confirmed |
| Prototype demo | Real simulation/VCDs and 4:45 storyboard | [Hosted 4:53.7 demo](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing); P1–P5 sections spot-checked; signed-out browser replay not independently tested |

Generic Yosys cells do not establish FPGA LUT utilization or maximum MHz.
The 10 ns *simulation stimulus* is not hardware timing evidence. Direction
misprediction CPI excludes BTB target misses and other processor effects.

## Phase I marking (30% of overall grade)

| Deliverable | Marks | Status |
| --- | ---: | --- |
| IEEE-formatted project report: Abstract, Literature Review, Proposed Solution, Individual Contributions, References | 10 | [PDF committed](../report/Phase1_IEEE_Report.pdf); separate author signoff still requires evidence |
| Prototype video (<=5 minutes; introduce all five members) | 15 | [4:53.7 MP4 published](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing); H.264/AAC and P1–P5 sections spot-checked |
| GitHub repository with report, video URL, authentic code/history/evidence | 5 | PR history, PDF, and video URL present; submission receipt received 16 Nov |

## Final signoff

- [x] All original contributor PRs #1–#7 merged and main CI passed.
- [x] BHT, BTB, control, traces, generic synthesis and illustrative CPI evidence available.
- [x] Verify BPU 16/32-entry regression (140 checks) and seven-top Yosys synthesis on QA branch.
- [x] Merge integrated BPU QA PR #8; successful merged-main CI recorded at `ee7f45c`.
- [ ] Run `make test`, `make synth-all`, `make metrics test-p5-metrics` on final merged main.
- [ ] Select a valid target timing flow or confirm with faculty that unmeasured Fmax may be disclosed.
- [ ] Verify full names, affiliations, source citations and all five authors' section approvals.
- [x] Commit `report/Phase1_IEEE_Report.pdf` via merged PR #15.
- [ ] Record independent final rendered-PDF/page inspection and complete all-author acknowledgment checks.
- [x] Host 4:53.7 MP4 with P1–P5 presentation segments and observed audio.
- [ ] Independently confirm original clip consents, all speaker identities, and signed-out browser playback.
- [x] Publish the same [recording URL](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing) in README and `video/DEMO_LINK.md`.
- [x] Submit the Phase I form; official Google Forms response receipt was received 16 Nov 2026 at 01:48 IST.
- [ ] Perform independent anonymous browser-playback and final post-merge checks, if needed for faculty signoff.

Phase II adds final Results/Discussion and Conclusion; do not present a full CPU,
fabricated timing, measured CPI, or unverifiable images as completed.
