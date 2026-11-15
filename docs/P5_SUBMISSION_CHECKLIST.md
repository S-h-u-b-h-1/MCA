# P5 final submission handoff — 16 November 2026

This is the current checklist; the dated engineering/review record is retained in [P5 review handoff](P5_REVIEW_HANDOFF.md). No faculty approval or coauthor consent is inferred from the receipt.

## Completed and evidenced

- [x] P1–P5 PRs #1–#7 merged; BPU QA #8, BTB evidence #13, P3 waveform evidence #14, and Phase I report #15 merged.
- [x] Existing hardware and metric verification: [main CI suite at `ee7f45c`](https://github.com/S-h-u-b-h-1/MCA/actions/runs/42348113271) and other successful workflows; locally recorded P5 tests, seven-top generic synthesis, and metric reconciliation are in `evidence/`.
- [x] The [final Phase I IEEE report](../report/Phase1_IEEE_Report.pdf) is committed. The README calls it approved for coursework submission by the team lead.
- [x] The [final team demonstration](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing) is uploaded. Original MP4 was inspected with `ffprobe`: 293.700 s (4:53.7), H.264/1080p + AAC audio. P1–P5 visual sections and audio presence were spot-checked.
- [x] Google Drive permissions show `Anyone with the link → Viewer`; the same URL appears in [README](../README.md) and [video/DEMO_LINK.md](../video/DEMO_LINK.md).
- [x] The team lead submitted the official Phase I Google Form; response receipt received at 01:48 IST on 16 November 2026.

## Remaining independent/administrative verification

- [ ] Confirm every author’s final section/affiliation approval; do not represent absent responses as received.
- [ ] Independently inspect the final rendered PDF page-by-page for layout and links if an updated copy is supplied.
- [ ] Obtain a faculty decision on the disclosed **unmeasured Fmax** or perform a supported target-specific timing flow.
- [ ] Independently play the hosted video in a signed-out browser, verify full narration and confirm original member clip handoff/consent.
- [ ] Re-run the complete tests/synthesis/metrics on the latest merged main, if needed for the faculty's final acceptance record; the last documented full main CI suite predates PRs #13–#15.

**Accuracy and timing caveat:** 130 branches are synthetic deterministic traces, CPI is illustrative, and Yosys generic cells are not FPGA LUTs nor frequency measurements.
