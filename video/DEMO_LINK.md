# Final Phase I prototype demonstration

**Watch video:** [MCA — Dynamic Branch Prediction Unit (Project 5)](https://drive.google.com/file/d/1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU/view?usp=sharing)

- **Google Drive file:** `MCA.mp4` (file ID `1keXnkWQt3XM15Cudw4f7V6h63R3U_sLU`).
- **Permissions verified on 16 November 2026:** `Anyone with the link` → `Viewer` (read-only; no specific reviewer invite required).
- **Media inspected:** downloaded original MP4, `ffprobe` reports **293.700 s (4:53.7)**, **1920 × 1080 H.264** video and **AAC 48 kHz** audio. This is under the five-minute Phase I ceiling.
- **Content spot-check:** visual samples cover the P1–P5 sections: BHT, BTB, next-PC/recovery, benchmark comparison, and synthesis/metrics. Audio is present in sampled portions of each section.
- **Verification limits:** sharing settings and media properties were independently verified; a separate signed-out Google browser playback and each speaker's identity/approval were not independently verified.

## Synthesis version note

The P5 video capture contains a **local Yosys 0.70+post** generic synthesis summary with **2,907 cells** for `branch_prediction_unit`. The [committed CI evidence](../evidence/synthesis/summary.md) uses **Yosys 0.33** and records **2,993 generic cells** for the same top. These are **different tool versions/flows**; the figures must not be treated as one controlled hardware-resource comparison. Neither is a device-mapped FPGA LUT count or measured maximum frequency.

The hosted file is linked from [README](../README.md). Keep the original upload unchanged to avoid breaking the faculty submission. The prototype is not a complete CPU; generic Yosys resource counts are not FPGA LUT utilization or a measured Fmax.
