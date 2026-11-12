#!/usr/bin/env python3
"""
render_bpu_waveform.py
Renders digital waveform diagrams directly from results/bpu_integration.vcd using Matplotlib.

Visualizes the integrated Branch Prediction Unit (branch_prediction_unit.v):
  - Speculative Fetch Stage: fetch_pc, 2-bit prediction_state, predicted_taken,
    btb_hit, predicted_target, speculative predicted_next_pc
  - Resolution Stage: resolve_valid, resolve_pc, resolve_actual_taken,
    resolve_actual_target, mispredict, flush, redirect, redirect_pc
  - Next-PC Muxing Priority: selected_next_pc prioritizing redirect_pc over predicted_next_pc
  - Demonstrates:
      1. Cold miss fallback to PC+4
      2. Misprediction redirect & pipeline flush (NT -> Taken)
      3. Correct taken+BTB-hit combinational next-PC selection, with no recovery redirect in this test case
      4. Target misprediction redirect (retraining BTB on target mismatch)
      5. Direction misprediction recovery to PC+4 (Taken -> NT)

Provenance & Authorship:
  - Source VCD: results/bpu_integration.vcd generated from testbench/tb_branch_prediction_unit.sv via 'make test-bpu'
  - Note on VCD dump: 'make test-bpu' executes two regression passes (INDEX_BITS=4 and INDEX_BITS=5).
    Pass 2 overwrites results/bpu_integration.vcd, so this waveform visualizes the INDEX_BITS=5
    (32-entry BHT, 32-entry BTB) configuration.
  - RTL Authorship:
      * BPU Top-Level Synthesizable Wrapper (branch_prediction_unit.v): Shubhaang (@S-h-u-b-h-1, PR #8)
      * P1 2-bit BHT (predictor_2bit.v, branch_history_table.v): Shubhaang (@S-h-u-b-h-1)
      * P2 Tagged BTB (branch_target_buffer.v): Tanish (@tanishrao13)
      * P3 Control (next_pc_mux.v, branch_resolution.v): Tanmay Singh (@tanmay-7706)
  - Evidence Capture & Renderer: Tanmay Singh (@tanmay-7706)
  - Timing Notice: Simulated 10 ns testbench clock (not measured hardware Fmax).
"""

import os
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

_SCRIPTS_DIR = str(Path(__file__).resolve().parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from vcd_parser import parse_vcd_header, parse_vcd_transitions


def render_bpu_waveform():
    vcd_path = "results/bpu_integration.vcd"
    if not os.path.exists(vcd_path):
        print(f"Error: {vcd_path} not found. Run 'make test-bpu' first.", file=sys.stderr)
        sys.exit(1)

    target_scope = "tb_branch_prediction_unit"
    required_signals = [
        "clk",
        "reset",
        "fetch_pc",
        "prediction_state",
        "predicted_taken",
        "btb_hit",
        "predicted_target",
        "predicted_next_pc",
        "resolve_valid",
        "resolve_pc",
        "resolve_actual_taken",
        "resolve_actual_target",
        "mispredict",
        "flush",
        "redirect",
        "redirect_pc",
        "selected_next_pc",
    ]

    timescale_str, timescale_ns, resolved_signals = parse_vcd_header(
        vcd_path, target_scope, required_signals
    )

    sym_map = {name: resolved_signals[name][0] for name in required_signals}
    transitions = parse_vcd_transitions(vcd_path, sym_map)

    target_vars = [
        ("clk", False, "#00ffcc", "Clock (Simulated 10 ns testbench clock)"),
        ("reset", False, "#ff3366", "Synchronous reset"),
        ("fetch_pc", True, "#00d4ff", "Speculative fetch PC [31:0]"),
        ("prediction_state", "state", "#ffaa00", "BHT 2-bit counter state"),
        ("predicted_taken", False, "#33ff99", "BHT predicted direction"),
        ("btb_hit", False, "#33ff99", "BTB cache tag match hit"),
        ("predicted_target", True, "#00ffcc", "BTB cached target [31:0]"),
        ("predicted_next_pc", True, "#70d6ff", "Speculative Next-PC mux output [31:0]"),
        ("resolve_valid", False, "#ffff00", "Branch resolution valid in EX stage"),
        ("resolve_pc", True, "#ffd166", "Resolved branch PC [31:0]"),
        ("resolve_actual_taken", False, "#ff9f1c", "Actual branch condition outcome"),
        ("resolve_actual_target", True, "#ff9f1c", "Actual computed branch target [31:0]"),
        ("mispredict", False, "#ff3366", "Branch misprediction detected"),
        ("flush", False, "#ff3366", "Pipeline squash / flush strobe"),
        ("redirect", False, "#ff3366", "Fetch redirect strobe"),
        ("redirect_pc", True, "#ff99bb", "Recovery redirect target PC [31:0]"),
        ("selected_next_pc", True, "#33ff99", "Next PC selected for fetch stage [31:0]"),
    ]

    t_min_ns = 20.0
    t_max_ns = 125.0
    t_min_raw = int(t_min_ns / timescale_ns)
    t_max_raw = int(t_max_ns / timescale_ns)

    def get_val_at(sym, t_raw):
        hist = transitions[sym]
        last_val = "0"
        for ct, val in hist:
            if ct <= t_raw:
                last_val = val
            else:
                break
        return last_val

    def fmt_hex(val_str):
        try:
            val_int = int(val_str, 2)
            return f"0x{val_int:08X}"
        except Exception:
            return val_str

    state_labels = {
        "0": "00 (SNT)",
        "00": "00 (SNT)",
        "1": "01 (WNT)",
        "01": "01 (WNT)",
        "10": "10 (WT)",
        "11": "11 (ST)",
    }

    fig, ax = plt.subplots(figsize=(17, 12), dpi=180)
    fig.patch.set_facecolor("#12131a")
    ax.set_facecolor("#181a24")

    y_spacing = 1.85
    n_sigs = len(target_vars)

    # Background alternating row shades
    for i in range(n_sigs):
        y_base = (n_sigs - 1 - i) * y_spacing
        if i % 2 == 0:
            ax.axhspan(y_base - 0.35, y_base + 1.35, color="#1e212f", alpha=0.5, zorder=0)

    # Time grid lines
    for t_ns in range(int(t_min_ns), int(t_max_ns) + 1, 5):
        ax.axvline(
            t_ns,
            color="#2d3142",
            linestyle=":" if t_ns % 10 != 0 else "--",
            linewidth=0.8 if t_ns % 10 != 0 else 1.0,
            alpha=0.7,
            zorder=1,
        )

    # Annotate test phases across the top without zero-stall / physical core claims
    phases = [
        (20, 39, "#00d4ff", "Phase 1: Cold Fetch\n[BHT=01, BTB miss, npc=PC+4 (0x1004)]"),
        (39, 49, "#ff3366", "Phase 2: Mispredict NT->Taken\n[flush=1, redirect=1 to 0x2000]"),
        (
            49,
            70,
            "#33ff99",
            "Phase 3: Correct Prediction (Taken + BTB Hit)\n[correct taken+BTB-hit combinational next-PC selection,\nwith no recovery redirect in this test case]",
        ),
        (70, 90, "#ffaa00", "Phase 4: Target Mispredict\n[Actual target 0x3000, redirect to 0x3000]"),
        (90, 115, "#ff5577", "Phase 5: Mispredict Taken->NT\n[flush=1, redirect to PC+4 (0x1004)]"),
        (115, 125, "#bb99ff", "Phase 6: Direction Decay\n[State weakens 10->01, pred switches NT]"),
    ]

    for t_start, t_end, col, text in phases:
        ax.axvspan(t_start, t_end, color=col, alpha=0.08, zorder=0)
        ax.text(
            (t_start + t_end) / 2.0,
            n_sigs * y_spacing + 0.38,
            text,
            color=col,
            fontsize=8.0,
            fontweight="bold",
            ha="center",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#161922", edgecolor=col, alpha=0.9),
        )

    for i, (name, kind, color, desc) in enumerate(target_vars):
        y_base = (n_sigs - 1 - i) * y_spacing
        sym = sym_map[name]

        # Label on left
        ax.text(
            t_min_ns - 1.2,
            y_base + 0.45,
            name,
            color="#e0e2ec",
            fontsize=9.2,
            fontfamily="monospace",
            fontweight="bold",
            ha="right",
            va="center",
        )

        hist = transitions[sym]
        points = []
        v_init = get_val_at(sym, t_min_raw)
        points.append((t_min_ns, v_init))

        for ct, val in hist:
            if t_min_raw <= ct <= t_max_raw:
                points.append((ct * timescale_ns, val))
        points.append((t_max_ns, points[-1][1]))

        if kind is False:
            # 1-bit digital waveform
            x_pts = []
            y_pts = []
            for idx in range(len(points) - 1):
                t_curr = points[idx][0]
                v_curr = 1.0 if points[idx][1] == "1" else 0.0
                t_next = points[idx + 1][0]
                x_pts.extend([t_curr, t_next])
                y_pts.extend([y_base + v_curr * 0.9, y_base + v_curr * 0.9])
            ax.step(x_pts, y_pts, where="post", color=color, linewidth=1.6, zorder=3)

        elif kind == "state":
            for idx in range(len(points) - 1):
                t_start = points[idx][0]
                t_end = points[idx + 1][0]
                val = points[idx][1]
                if t_end - t_start < 0.1:
                    continue
                st_text = state_labels.get(val, val)
                is_taken = val in ("10", "11")
                fill_color = "#1f382a" if is_taken else "#382226"
                edge_color = "#00ff88" if is_taken else "#ff5577"

                h = 0.85
                y_m = y_base + 0.45
                dt = 0.3 if (t_end - t_start) > 0.8 else (t_end - t_start) * 0.25
                poly_x = [t_start, t_start + dt, t_end - dt, t_end, t_end - dt, t_start + dt]
                poly_y = [y_m, y_m + h / 2, y_m + h / 2, y_m, y_m - h / 2, y_m - h / 2]

                poly = patches.Polygon(
                    list(zip(poly_x, poly_y)),
                    facecolor=fill_color,
                    edgecolor=edge_color,
                    linewidth=1.4,
                    zorder=2,
                )
                ax.add_patch(poly)
                if t_end - t_start >= 3.0:
                    ax.text(
                        (t_start + t_end) / 2.0,
                        y_m,
                        st_text,
                        color="#ffffff",
                        fontsize=7.5,
                        fontfamily="monospace",
                        fontweight="bold",
                        ha="center",
                        va="center",
                        zorder=4,
                    )

        elif kind is True:
            for idx in range(len(points) - 1):
                t_start = points[idx][0]
                t_end = points[idx + 1][0]
                val = points[idx][1]
                if t_end - t_start < 0.1:
                    continue
                hex_str = fmt_hex(val)
                h = 0.8
                y_m = y_base + 0.45
                dt = 0.3 if (t_end - t_start) > 0.8 else (t_end - t_start) * 0.25
                poly_x = [t_start, t_start + dt, t_end - dt, t_end, t_end - dt, t_start + dt]
                poly_y = [y_m, y_m + h / 2, y_m + h / 2, y_m, y_m - h / 2, y_m - h / 2]

                is_active_target = hex_str not in ("0x00000000", "0xXXXXXXXX")
                fill_color = "#222938" if is_active_target else "#181b24"
                edge_color = color if is_active_target else "#4e5568"

                poly = patches.Polygon(
                    list(zip(poly_x, poly_y)),
                    facecolor=fill_color,
                    edgecolor=edge_color,
                    linewidth=1.2,
                    zorder=2,
                )
                ax.add_patch(poly)

                if t_end - t_start >= 4.0:
                    ax.text(
                        (t_start + t_end) / 2.0,
                        y_m,
                        hex_str,
                        color="#ffffff",
                        fontsize=7.3,
                        fontfamily="monospace",
                        fontweight="semibold",
                        ha="center",
                        va="center",
                        zorder=4,
                    )

    ax.set_xlim(t_min_ns - 15.0, t_max_ns + 1.0)
    ax.set_ylim(-1.0, (n_sigs + 2.2) * y_spacing)

    # Format time axis explicitly noting simulated clock vs physical hardware Fmax
    ax.set_xlabel(
        "Simulation Time (ns) [Simulated 10 ns testbench clock (not measured hardware Fmax)]",
        fontsize=9.5,
        color="#a0a6b8",
        labelpad=10,
    )
    ticks = list(range(int(t_min_ns), int(t_max_ns) + 1, 10))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t} ns" for t in ticks], color="#a0a6b8", fontsize=8.5)

    ax.get_yaxis().set_visible(False)
    for spine in ax.spines.values():
        spine.set_color("#2d3142")

    plt.title(
        f"Integrated Branch Prediction Unit Simulation Waveform (tb_branch_prediction_unit.sv / results/bpu_integration.vcd)\n"
        f"VCD Provenance: results/bpu_integration.vcd from make test-bpu pass 2 (INDEX_BITS=5: 32 BHT entries, 32 BTB sets; timescale: {timescale_str})\n"
        f"RTL Authorship: BPU Wrapper & P1 BHT: Shubhaang (@S-h-u-b-h-1); P2 BTB: Tanish (@tanishrao13); P3 Control: Tanmay (@tanmay-7706)\n"
        f"Evidence Capture & Rendering: Tanmay Singh (@tanmay-7706) | Simulated 10 ns testbench stimulus",
        color="#ffffff",
        fontsize=10.5,
        fontweight="bold",
        pad=36,
    )

    plt.tight_layout()
    out_file = "evidence/waveforms/bpu_integration.png"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    plt.savefig(out_file, dpi=180, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    if not os.path.exists(out_file) or os.path.getsize(out_file) == 0:
        print(f"Error: Failed to write {out_file} or file is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully rendered genuine BPU integration waveform evidence: {out_file} ({os.path.getsize(out_file)} bytes)")


if __name__ == "__main__":
    render_bpu_waveform()
