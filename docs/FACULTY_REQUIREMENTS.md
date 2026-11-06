# Faculty requirements and evidence gates — MCA Project 5

**Source:** [Modern Computer Architecture Project 5](https://docs.google.com/document/d/1CoQOY3T4p0qY1B9qR3WPh8I93aCyN-zIs9VF17kBMNU/edit).
Phase I deadline: **16 November 2026, 11:59 PM IST**.

## Current implementation

P1–P5 contributions (PRs #1–#7) were merged and all six workflows passed on
main commit `97c8290` (5 November 2026). This is a branch-direction/target
prediction **prototype**, not a complete pipelined CPU. The final QA branch adds
a synthesizable integrated BPU wrapper; verify/merge its PR before claiming it
as part of main.

| Faculty objective | Evidence | Remaining |
| --- | --- | --- |
| 2-bit BHT, baseline 1-bit/static predictors | P1/P4 RTL, self-checking unit and independent scoreboards | None for module-level scope |
| Tagged BTB | P2 RTL, directed and parameterized tests | Include hit/miss/alias evidence in demo |
| Next PC, mispredict/flush/redirect | P3 modules and interface-level integration; proposed synthesized BPU wrapper | Verify new wrapper CI and merge |
| BEQ/BNE loop-oriented traces | 130 synthetic branches with HDL/Python parity | Disclose deterministic trace and cold-start limits |
| Accuracy/CPI | `evidence/metrics/accuracy.csv`, `accuracy.svg`, `cpi_assumptions.md` | CPI is illustrative, not CPU-measured |
| Logic resources | Six-top Yosys generic synthesis, source hashes/CI artifacts | Reproduce seven-top synthesis after BPU QA merge |
| Maximum frequency | No selected FPGA, constraints or post-route timing report | **Unmeasured**; agree valid target flow or faculty-approved limitation |
| IEEE technical report | P3/P4/P5 draft sections, P1/P2 design notes | Final all-author-reviewed IEEE PDF missing |
| Prototype demo | Real simulation/VCDs and 4:45 storyboard | Real five-member recording and accessible URL missing |

Generic Yosys cells do not establish FPGA LUT utilization or maximum MHz.
The 10 ns *simulation stimulus* is not hardware timing evidence. Direction
misprediction CPI excludes BTB target misses and other processor effects.

## Phase I marking (30% of overall grade)

| Deliverable | Marks | Status |
| --- | ---: | --- |
| IEEE-formatted project report: Abstract, Literature Review, Proposed Solution, Individual Contributions, References | 10 | `report/Phase1_IEEE_Report.pdf` pending |
| Prototype video (<=5 minutes; introduce all five members) | 15 | Storyboard prepared; real hosted video pending |
| GitHub repository with report, video URL, authentic code/history/evidence | 5 | PR history/code/CI present; final PDF and video link still needed |

## Final signoff

- [x] All original contributor PRs #1–#7 merged and main CI passed.
- [x] BHT, BTB, control, traces, generic synthesis and illustrative CPI evidence available.
- [ ] Run/merge final integrated BPU QA PR after its CI and seven-top synthesis pass.
- [ ] Run `make test`, `make synth-all`, `make metrics test-p5-metrics` on final merged main.
- [ ] Select a valid target timing flow or confirm with faculty that unmeasured Fmax may be disclosed.
- [ ] Verify full names, affiliations, source citations and all five authors' section approvals.
- [ ] Compile, visually check and commit `report/Phase1_IEEE_Report.pdf`.
- [ ] Record/edit real 4:30–4:50 demo; introduce all five, show live proof, host accessible link.
- [ ] Update README and `video/DEMO_LINK.md` with the same verified recording URL.
- [ ] Verify report/video/evidence links, then [submit the Phase I form](https://docs.google.com/forms/d/e/1FAIpQLSc6Cx8OrOQLGj_X2ZMkyG5jc8mokq36mGRq2x8jGRNV1sbegA/viewform) before deadline.

Phase II adds final Results/Discussion and Conclusion; do not present a full CPU,
fabricated timing, measured CPI, or unverifiable images as completed.
