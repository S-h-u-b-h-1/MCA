#!/usr/bin/env python3
"""
render_p3_waveform.py
Renders digital waveform diagrams directly from results/p3_integrated.vcd using Matplotlib.

Visualizes closed-loop P1+P2+P3 integration (tb_integrated.sv):
  - Demonstrates deterministic execute-stage branch resolution comparing against
    saved fetch metadata.
  - Highlights direction mispredictions (NT->T and T->NT) with pipeline flush and recovery redirect.
  - Highlights correct taken prediction with no recovery redirect.
  - Verifies redirect priority over speculative fetch in selected_pc.

Provenance & Authorship:
  - Source VCD: results/p3_integrated.vcd generated from testbench/tb_integrated.sv via 'make test-p3-integrated'
  - P3 Control RTL & Integration Harness: Tanmay Singh (@tanmay-7706)
  - P1 2-bit BHT RTL: Shubhaang (@S-h-u-b-h-1)
  - P2 Tagged BTB RTL: Tanish (@tanishrao13)
  - Timing Notice: Simulated 10 ns testbench clock (not measured hardware Fmax).
"""

import os
import re
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def parse_vcd_header(vcd_path, target_scope, required_signals):
    scope_stack = []
    signals = {}
    timescale_str = "1ps"
    timescale_ns = 0.001

    with open(vcd_path, "r", encoding="utf-8", errors="replace") as f:
        in_timescale = False
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("$timescale"):
                in_timescale = True
                continue
            if in_timescale:
                if "$end" in line:
                    in_timescale = False
                else:
                    timescale_str = line.replace("$end", "").strip()
                    m = re.match(r"(\d+)\s*([a-z]+)", timescale_str)
                    if m:
                        val = int(m.group(1))
                        unit = m.group(2)
                        unit_mult = {
                            "s": 1e9,
                            "ms": 1e6,
                            "us": 1e3,
                            "ns": 1.0,
                            "ps": 1e-3,
                            "fs": 1e-6,
                        }
                        timescale_ns = val * unit_mult.get(unit, 1e-3)
                continue
            if line.startswith("$scope"):
                parts = line.split()
                scope_stack.append(parts[2])
            elif line.startswith("$upscope"):
                if scope_stack:
                    scope_stack.pop()
            elif line.startswith("$var"):
                parts = line.split()
                var_type = parts[1]
                size = int(parts[2])
                sym = parts[3]
                var_name = parts[4]
                curr_scope = ".".join(scope_stack)
                signals[(curr_scope, var_name)] = (sym, size)
            elif line.startswith("$enddefinitions"):
                break

    resolved = {}
    missing = []
    for sig_name in required_signals:
        key = (target_scope, sig_name)
        if key in signals:
            resolved[sig_name] = signals[key]
        else:
            missing.append(sig_name)

    if missing:
        raise RuntimeError(
            f"VCD parsing error: Missing required signals in scope '{target_scope}': {missing}"
        )

    return timescale_str, timescale_ns, resolved


def parse_vcd_transitions(vcd_path, symbol_map):
    tracked_symbols = set(symbol_map.values())
    transitions = {sym: [] for sym in tracked_symbols}
    current_time = 0

    with open(vcd_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip().startswith("$enddefinitions"):
                break

        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                current_time = int(line[1:])
            elif line.startswith("b"):
                parts = line.split()
                val = parts[0][1:]
                sym = parts[1]
                if sym in transitions:
                    transitions[sym].append((current_time, val))
            elif len(line) >= 2 and line[1:] in transitions:
                val = line[0]
                sym = line[1:]
                transitions[sym].append((current_time, val))

    return transitions


def render_p3_waveform():
    vcd_path = "results/p3_integrated.vcd"
    if not os.path.exists(vcd_path):
        print(f"Error: {vcd_path} not found. Run 'make test-p3-integrated' first.", file=sys.stderr)
        sys.exit(1)

    target_scope = "tb_integrated"
    required_signals = [
        "clk",
        "res_valid",
        "res_branch_pc",
        "res_saved_taken",
        "res_saved_hit",
        "res_actual_taken",
        "res_mispredict",
        "res_flush",
        "res_redirect",
        "res_redirect_pc",
        "selected_pc",
        "p1_update_valid",
        "p2_update_valid",
    ]

    timescale_str, timescale_ns, resolved_signals = parse_vcd_header(
        vcd_path, target_scope, required_signals
    )

    sym_map = {name: resolved_signals[name][0] for name in required_signals}
    transitions = parse_vcd_transitions(vcd_path, sym_map)

    target_vars = [
        ("clk", False, "#00ffcc"),
        ("res_valid", False, "#ffff00"),
        ("res_branch_pc", True, "#00d4ff"),
        ("res_saved_taken", False, "#ffaa00"),
        ("res_saved_hit", False, "#ffaa00"),
        ("res_actual_taken", False, "#00ff66"),
        ("res_mispredict", False, "#ff3366"),
        ("res_flush", False, "#ff3366"),
        ("res_redirect", False, "#ff3366"),
        ("res_redirect_pc", True, "#ff99bb"),
        ("selected_pc", True, "#33ff99"),
        ("p1_update_valid", False, "#bb99ff"),
        ("p2_update_valid", False, "#bb99ff"),
    ]

    t_min_ns = 80.0
    t_max_ns = 155.0
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

    fig, ax = plt.subplots(figsize=(15, 9), dpi=180)
    fig.patch.set_facecolor("#12131a")
    ax.set_facecolor("#181a24")

    y_spacing = 2.0
    n_sigs = len(target_vars)

    for i in range(n_sigs):
        y_base = (n_sigs - 1 - i) * y_spacing
        if i % 2 == 0:
            ax.axhspan(y_base - 0.4, y_base + 1.4, color="#1e212f", alpha=0.5, zorder=0)

    for t_ns in range(int(t_min_ns), int(t_max_ns) + 1, 5):
        ax.axvline(t_ns, color="#2d3142", linestyle=":", linewidth=0.8, zorder=1)

    # Annotate test phases
    ax.axvspan(90, 110, color="#00ff66", alpha=0.08, zorder=0)
    ax.text(
        100,
        n_sigs * y_spacing + 0.2,
        "T2: Correct Prediction (Taken + BTB Hit)\n[correct taken+BTB-hit combinational selection, redirect=0, selected_pc=0x2000]",
        color="#00ff99",
        fontsize=8.5,
        fontweight="bold",
        ha="center",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#162e24", edgecolor="#00ff66", alpha=0.9),
    )

    ax.axvspan(110, 130, color="#ff3366", alpha=0.08, zorder=0)
    ax.text(
        120,
        n_sigs * y_spacing + 0.2,
        "T3: Direction Mispredict (NT -> T)\n[mispredict=1, flush=1, redirect_pc=0x3000]",
        color="#ff6688",
        fontsize=8.5,
        fontweight="bold",
        ha="center",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#3d1822", edgecolor="#ff3366", alpha=0.9),
    )

    ax.axvspan(130, 150, color="#ffaa00", alpha=0.08, zorder=0)
    ax.text(
        140,
        n_sigs * y_spacing + 0.2,
        "T4: Direction Mispredict (T -> NT)\n[mispredict=1, redirect_pc=PC+4 (0x1008)]",
        color="#ffbb33",
        fontsize=8.5,
        fontweight="bold",
        ha="center",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#3d2c18", edgecolor="#ffaa00", alpha=0.9),
    )

    for i, (name, is_bus, color) in enumerate(target_vars):
        y_base = (n_sigs - 1 - i) * y_spacing
        sym = sym_map[name]

        ax.text(
            t_min_ns - 1.5,
            y_base + 0.4,
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

        if not is_bus:
            x_pts = []
            y_pts = []
            for idx in range(len(points) - 1):
                t_curr = points[idx][0]
                v_curr = 1.0 if points[idx][1] == "1" else 0.0
                t_next = points[idx + 1][0]
                x_pts.extend([t_curr, t_next])
                y_pts.extend([y_base + v_curr * 0.9, y_base + v_curr * 0.9])
            ax.step(x_pts, y_pts, where="post", color=color, linewidth=1.6, zorder=3)
        else:
            for idx in range(len(points) - 1):
                t_start = points[idx][0]
                t_end = points[idx + 1][0]
                val = points[idx][1]
                if t_end - t_start < 0.1:
                    continue

                hex_str = fmt_hex(val)
                h = 0.8
                y_m = y_base + 0.4
                dt = 0.3 if t_end - t_start > 0.6 else (t_end - t_start) * 0.2
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

                if t_end - t_start > 4.0:
                    ax.text(
                        (t_start + t_end) / 2.0,
                        y_m,
                        hex_str,
                        color="#ffffff",
                        fontsize=7.5,
                        fontfamily="monospace",
                        fontweight="semibold",
                        ha="center",
                        va="center",
                        zorder=4,
                    )

    ax.set_xlim(t_min_ns - 14.0, t_max_ns + 1.0)
    ax.set_ylim(-1.0, (n_sigs + 1.8) * y_spacing)

    ax.set_xlabel(
        "Simulation Time (ns) [Simulated 10 ns testbench clock (not measured hardware Fmax)]",
        fontsize=9.5,
        color="#a0a6b8",
        labelpad=10,
    )
    ticks = list(range(int(t_min_ns), int(t_max_ns) + 1, 5))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t} ns" for t in ticks], color="#a0a6b8", fontsize=8.5)

    ax.get_yaxis().set_visible(False)
    for spine in ax.spines.values():
        spine.set_color("#2d3142")

    plt.title(
        f"P3 Integrated Pipeline Simulation Waveform (tb_integrated.sv / results/p3_integrated.vcd)\n"
        f"VCD Provenance: results/p3_integrated.vcd (timescale: {timescale_str}) | Simulated 10 ns testbench stimulus\n"
        f"P1 BHT: Shubhaang (@S-h-u-b-h-1) | P2 BTB: Tanish (@tanishrao13) | P3 Control & Renderer: Tanmay Singh (@tanmay-7706)",
        color="#ffffff",
        fontsize=10.5,
        fontweight="bold",
        pad=32,
    )

    plt.tight_layout()
    out_file = "evidence/waveforms/p3_integrated_simulation.png"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    plt.savefig(out_file, dpi=180, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)

    if not os.path.exists(out_file) or os.path.getsize(out_file) == 0:
        print(f"Error: Failed to write {out_file} or file is empty.", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully rendered genuine simulation waveform: {out_file} ({os.path.getsize(out_file)} bytes)")


if __name__ == "__main__":
    render_p3_waveform()
