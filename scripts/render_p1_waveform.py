#!/usr/bin/env python3
"""
render_p1_waveform.py
Renders digital waveform diagrams directly from results/p1_bht.vcd using Matplotlib.

Visualizes:
  - 2-bit saturating counter state transitions: 01 (Weak NT) -> 10 (Weak T) -> 11 (Strong T)
    -> 11 (Saturate) -> 10 (Weak T) -> 01 (Weak NT) -> 00 (Strong NT) -> 00 (Saturate)
  - Synchronous reset deassertion and recovery back to weakly not-taken (01)
  - Actual taken / update pulse timing
  - Prediction output (predict_taken) alignment with state[1]
  - Independent indexing (PC_B = 0x104 vs PC_A = 0x100) and index aliasing

Provenance & Authorship:
  - VCD Source: results/p1_bht.vcd generated from testbench/tb_p1_bht.sv via 'make test-p1'
  - P1 RTL Authorship: Shubhaang (@S-h-u-b-h-1) [rtl/predictor_2bit.v, rtl/branch_history_table.v]
  - Evidence Capture & Renderer: Tanmay Singh (@tanmay-7706, Person 3: Control Integration)
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


def render_p1_waveform():
    vcd_path = "results/p1_bht.vcd"
    if not os.path.exists(vcd_path):
        print(f"Error: {vcd_path} not found. Run 'make test-p1' first.", file=sys.stderr)
        sys.exit(1)

    target_scope = "tb_p1_bht"
    required_signals = [
        "clk",
        "reset",
        "lookup_pc",
        "prediction_state",
        "predict_taken",
        "update_valid",
        "update_pc",
        "actual_taken",
    ]

    timescale_str, timescale_ns, resolved_signals = parse_vcd_header(
        vcd_path, target_scope, required_signals
    )

    sym_map = {name: resolved_signals[name][0] for name in required_signals}
    transitions = parse_vcd_transitions(vcd_path, sym_map)

    # Signal display configuration: (name, kind, color, description)
    signal_configs = [
        ("clk", False, "#00ffcc", "clk (Simulated 10 ns testbench clock)"),
        ("reset", False, "#ff3366", "reset (Synchronous reset)"),
        ("lookup_pc", True, "#00d4ff", "lookup_pc [31:0] (Branch address)"),
        ("prediction_state", "state", "#ffaa00", "prediction_state [1:0] (2-bit BHT state)"),
        ("predict_taken", False, "#33ff99", "predict_taken (state[1] direction)"),
        ("update_valid", False, "#bb99ff", "update_valid (BHT update strobe)"),
        ("update_pc", True, "#00b4d8", "update_pc [31:0] (Update address)"),
        ("actual_taken", False, "#ffdd55", "actual_taken (Architectural outcome)"),
    ]

    # Time window: 10 ns to 118 ns (relative to testbench timescale)
    # timescale_ns is 0.001 ns for 1ps, so 10 ns = 10000 time units
    t_min_ns = 10.0
    t_max_ns = 118.0
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
        "0": "00 (Strong NT)",
        "00": "00 (Strong NT)",
        "1": "01 (Weak NT)",
        "01": "01 (Weak NT)",
        "10": "10 (Weak T)",
        "11": "11 (Strong T)",
    }

    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=180)
    fig.patch.set_facecolor("#12131a")
    ax.set_facecolor("#181a24")

    y_spacing = 1.9
    n_sigs = len(signal_configs)

    # Background alternating row shades
    for i in range(n_sigs):
        y_base = (n_sigs - 1 - i) * y_spacing
        if i % 2 == 0:
            ax.axhspan(y_base - 0.35, y_base + 1.35, color="#1e212f", alpha=0.5, zorder=0)

    # Time grid lines every 5 ns (simulated half-cycles)
    for t_ns in range(int(t_min_ns), int(t_max_ns) + 1, 5):
        ax.axvline(
            t_ns,
            color="#2d3142",
            linestyle=":" if t_ns % 10 != 0 else "--",
            linewidth=0.8 if t_ns % 10 != 0 else 1.0,
            alpha=0.7,
            zorder=1,
        )

    # Annotate test phases across the top
    phases = [
        (10, 20, "#ff3366", "Reset Deassert\n[State=01 Weak NT]"),
        (20, 50, "#33ff99", "Train Taken (01 -> 10 -> 11 -> Sat 11)\n[actual_taken=1, predict switches to 1]"),
        (50, 90, "#ffaa00", "Train Not-Taken (11 -> 10 -> 01 -> 00 -> Sat 00)\n[actual_taken=0, predict switches to 0]"),
        (90, 102, "#00d4ff", "Independent PC_B (0x104)\n[PC_B trains to 10; PC_A stays 00]"),
        (102, 118, "#bb99ff", "Index Aliasing Test\n[PC_ALIAS (0x140) maps to same BHT set]"),
    ]

    for t_start, t_end, col, text in phases:
        ax.axvspan(t_start, t_end, color=col, alpha=0.08, zorder=0)
        ax.text(
            (t_start + t_end) / 2.0,
            n_sigs * y_spacing + 0.35,
            text,
            color=col,
            fontsize=8.5,
            fontweight="bold",
            ha="center",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#161922", edgecolor=col, alpha=0.9),
        )

    for i, (name, kind, color, desc) in enumerate(signal_configs):
        y_base = (n_sigs - 1 - i) * y_spacing
        sym = sym_map[name]

        # Label on left
        ax.text(
            t_min_ns - 1.2,
            y_base + 0.45,
            name,
            color="#e0e2ec",
            fontsize=9.5,
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
            # 2-bit counter state bus with distinct color fill
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

                if t_end - t_start >= 3.5:
                    ax.text(
                        (t_start + t_end) / 2.0,
                        y_m,
                        st_text,
                        color="#ffffff",
                        fontsize=7.8,
                        fontfamily="monospace",
                        fontweight="bold",
                        ha="center",
                        va="center",
                        zorder=4,
                    )

        elif kind is True:
            # Multi-bit bus (lookup_pc, update_pc)
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

                fill_color = "#222938" if hex_str != "0x00000000" else "#181b24"
                edge_color = color if hex_str != "0x00000000" else "#4e5568"

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
                        fontsize=7.5,
                        fontfamily="monospace",
                        fontweight="bold",
                        ha="center",
                        va="center",
                        zorder=4,
                    )

    ax.set_xlim(t_min_ns - 14.0, t_max_ns + 1.0)
    ax.set_ylim(-1.0, (n_sigs + 1.8) * y_spacing)

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
        f"P1 2-Bit Saturating Counter BHT Simulation Waveform (tb_p1_bht.sv / results/p1_bht.vcd)\n"
        f"Independently Captured Verification Diagram for Shubhaang's P1 RTL (predictor_2bit.v / branch_history_table.v)\n"
        f"VCD Provenance: results/p1_bht.vcd (timescale: {timescale_str}) | Simulated 10 ns testbench stimulus\n"
        f"RTL Authorship: Shubhaang (@S-h-u-b-h-1) | Evidence Capture & Plotting: Tanmay Singh (@tanmay-7706)",
        color="#ffffff",
        fontsize=10.5,
        fontweight="bold",
        pad=34,
    )

    plt.tight_layout()
    out_file = "evidence/waveforms/p1_bht.png"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    plt.savefig(out_file, dpi=180, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    if not os.path.exists(out_file) or os.path.getsize(out_file) == 0:
        print(f"Error: Failed to write {out_file} or file is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully rendered genuine P1 waveform evidence: {out_file} ({os.path.getsize(out_file)} bytes)")


if __name__ == "__main__":
    render_p1_waveform()
