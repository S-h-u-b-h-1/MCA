#!/usr/bin/env bash
# Reproducible iCE40 software place-and-route timing, no physical FPGA required.
set -Eeuo pipefail
cd "$(dirname "$0")/.."

OUT="results/fpga_timing"
mkdir -p "$OUT"
LOG="$OUT/nextpnr-route.log"
NET="$OUT/bpu_fpga_timing_top.json"
ASC="$OUT/bpu_fpga_timing_top.asc"

for cmd in yosys nextpnr-ice40 python3; do
    command -v "$cmd" >/dev/null || { echo "Missing tool: $cmd" >&2; exit 2; }
done

{
    yosys -V
    nextpnr-ice40 --version
    python3 --version
} >"$OUT/tool_versions.txt" 2>&1

# Preserve the entire original P1/P2/P3 BPU RTL. Add only registered I/O for
# the clocked FPGA timing study. A false or absent timing result fails closed.
yosys -Q -T -l "$OUT/yosys-ice40.log" -p \
  "read_verilog rtl/branch_history_table.v rtl/predictor_2bit.v rtl/branch_target_buffer.v rtl/next_pc_mux.v rtl/branch_resolution.v rtl/branch_prediction_unit.v rtl/fpga_timing_harness.v; hierarchy -check -top bpu_fpga_timing_top; synth_ice40 -flatten -top bpu_fpga_timing_top -json $NET; check -assert; stat" >/dev/null

# No pinout/PCF is invented: unconstrained I/O pins are automatically placed.
# The 25 MHz clock is a routing TARGET (not a claimed result).
# --timing-allow-fail allows reporting a truthful lower achieved Fmax.
set -o pipefail
nextpnr-ice40 \
  --hx8k --package ct256 \
  --json "$NET" --asc "$ASC" \
  --pcf-allow-unconstrained \
  --freq 25 --seed 1 --timing-allow-fail \
  2>&1 | tee "$LOG"

python3 scripts/report_fpga_timing.py \
  --netlist "$NET" --asc "$ASC" --log "$LOG" \
  --tools "$OUT/tool_versions.txt" \
  --json-out "$OUT/summary.json" \
  --markdown-out "$OUT/report.md"

echo "Post-route timing artifact is ready: $OUT/report.md"
