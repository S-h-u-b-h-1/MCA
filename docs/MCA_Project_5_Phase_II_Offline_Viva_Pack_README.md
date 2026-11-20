# MCA Project 5 — Phase II Offline Viva Pack

**Team:** master-slave (Section C)  
**Evaluation:** 24 November 2026, 1:45–2:00 PM IST, A410.

The offline ZIP is available as **`MCA_Project_5_Phase_II_Complete_Offline_Viva_Pack.zip`** from the team lead's ChatGPT handoff. It was verified by ZIP CRC and includes SHA-256 checksums. **The 40 MB ZIP and formatted preparation PDFs are not committed to this GitHub repository.** GitHub hosts the readable preparation resources, the authoritative final technical report and evidence.

## Names of the handoff files

| Correct filename | Contents |
| --- | --- |
| `MCA_Project_5_Phase_II_Team_Preparation_Guide.pdf` | Full 13-page five-member technical viva guide |
| `MCA_Project_5_Phase_II_Team_Preparation_Guide.docx` | Editable version of the preparation guide |
| `MCA_Project_5_Phase_II_One_Page_Viva_Cheat_Sheet.pdf` | One-page last-minute revision |
| `MCA_Project_5_Phase_II_Complete_Offline_Viva_Pack.zip` | All above plus Phase II IEEE report/source, raw FPGA routing evidence and original Phase I demo MP4 |

## Readable equivalents in this repository

- [Team preparation guide](MCA_Project_5_Phase_II_Team_Preparation_Guide.md).
- [One-page cheat sheet](MCA_Project_5_Phase_II_One_Page_Viva_Cheat_Sheet.md).
- [15-minute live viva runbook](PHASE2_LIVE_VIVA_RUNBOOK.md).
- [Phase II IEEE report (PDF)](../report/Phase2_Final_IEEE_Report.pdf) and [editable IEEE LaTeX](../report/Phase2_Final_IEEE_Report.tex).
- [Phase II release status](PHASE2_RELEASE_STATUS.md).
- [Software FPGA timing evidence](../evidence/fpga_timing/POSTROUTE_RESULT.md).

## Verification and limitations

Source-backed 2-bit branch direction accuracy is **55/130** on three deterministic synthetic branch traces. FPGA mapped timing achieved a **93.22 MHz software post-route estimate** for an iCE40HX8K-CT256 registered BPU harness with **427 LUT4, 279 FF, 56 carry and 4 RAM blocks**. This is **not physical-board Fmax**, a complete CPU or measured application performance. Formal acceptance by the MCA instructor and final coauthor approvals must not be inferred from automated CI.

**Offline fallback:** Copy the ZIP to the demo laptop and extract it before 24 November. Show the report, short live BPU test, committed waveform and timing evidence. Do not rely on streaming the 4:54 team video during the strict 15-minute evaluation slot.
