# MCA Project 5 — Phase II One-Page Viva Cheat Sheet

**Team master-slave · Section C · Tuesday 24 November 2026 · 1:45–2:00 PM · A410**  
**Shubhaang Kataruka · Tanish Yadav · Tanmay Singh · Vansh Panwar · Lakshya**

### One-minute explanation
We built a **synthesizable Verilog branch-prediction subsystem**, not a complete CPU. A two-bit **BHT predicts direction**, a tagged **BTB predicts target**, a next-PC mux chooses **BTB target only if Taken AND BTB hit, else PC+4**, and recovery compares **saved fetch-time predictions** with resolved outcomes to generate **flush/redirect**.

### BHT counter (reset = 01; PC[5:2] indexes 16 entries)

| State | Predict | Actual Taken | Actual Not Taken |
|---|---|---|---|
| 00 strong NT | NT | 01 | 00 |
| 01 weak NT | NT | 10 | 00 |
| 10 weak T | T | 11 | 01 |
| 11 strong T | T | 11 | 10 |

T, T, NT, NT from 01 → before-update predictions **NT, T, T, T**; updated states **10, 11, 10, 01**. Aliasing example: **0x100 and 0x140** both index 0.

### Source-backed comparison (130 synthetic branches)

| Workload | Always NT | 1-bit | 2-bit |
|---|---:|---:|---:|
| Loop (40) | 8 | 24 | **31** |
| Alternating (40) | **20** | 0 | 0 |
| Mixed (50) | 20 | 23 | **24** |
| **Overall (130)** | **48 (36.92%)** | **47 (36.15%)** | **55 (42.31%)** |

Mixed 16→32-entry two-bit BHT: **24/50 → 37/50**. Model-only CPI = `1+0.2×miss_rate×3`; two-bit **1.346154**, not CPU-measured.

### FPGA timing: verified, but not physically measured

**iCE40HX8K-CT256** registered BPU harness: **estimated Fmax 93.22 MHz**; **period 10.73 ns**; **25 MHz target passed**. FPGA-mapped resources **427 LUT4 / 279 FF / 56 carry / 4 RAM blocks**. Critical path: BTB tag storage → hit/next-PC logic → observation register.

**Must qualify:** Yosys + nextpnr software post-route estimate. No physical FPGA test, full CPU, complete board I/O constraints or measured speedup. Faculty acceptance pending. Generic Yosys **2,993 cells** are not 427 FPGA LUTs.

### Rapid demo, in repository root

```bash
make test-bpu
make test-p4-compare
make metrics test-p5-metrics
# Optional, pre-run before the viva:
bash scripts/run_fpga_timing.sh
```

Open `evidence/waveforms/bpu_integration.png`, `evidence/metrics/accuracy.svg`, `evidence/fpga_timing/POSTROUTE_RESULT.md`.

**Owners:** Shubhaang—BHT; Tanish—BTB; Tanmay—recovery; Vansh—baselines/oracle; Lakshya—synthesis/metrics/report.

[Detailed guide](MCA_Project_5_Phase_II_Team_Preparation_Guide.md) · [Final report](../report/Phase2_Final_IEEE_Report.pdf) · [verified timing](../evidence/fpga_timing/POSTROUTE_RESULT.md).
