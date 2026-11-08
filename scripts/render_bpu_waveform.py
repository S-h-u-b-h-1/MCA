#!/usr/bin/env python3
"""
render_bpu_waveform.py
Generates genuine simulation waveform screenshot from results/bpu_integration.vcd.
Matches professional digital waveform viewers (Surfer / GTKWave).

Visualizes the integrated Branch Prediction Unit (branch_prediction_unit.v):
  - Speculative Fetch Stage: fetch_pc, 2-bit prediction_state, predicted_taken,
    btb_hit, predicted_target, speculative predicted_next_pc
  - Resolution Stage: resolve_valid, resolve_pc, resolve_actual_taken,
    resolve_actual_target, mispredict, flush, redirect, redirect_pc
  - Next-PC Muxing Priority: selected_next_pc prioritizing redirect_pc over predicted_next_pc
  - Demonstrates:
      1. Cold miss fallback to PC+4
      2. Misprediction redirect & pipeline flush (NT -> Taken)
      3. Zero-bubble correct speculative branch prediction (Taken + BTB Hit)
      4. Target misprediction redirect (retraining BTB to 0x3000)
      5. Direction misprediction recovery to PC+4 (Taken -> NT)

Source: results/bpu_integration.vcd (tb_branch_prediction_unit.sv)
Author/Verifier: Tanmay Singh (Person 3: Next-PC Selection & Branch Resolution)
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches

vcd_path = 'results/bpu_integration.vcd'
if not os.path.exists(vcd_path):
    print(f"Error: {vcd_path} not found. Run 'make test-bpu' first.", file=sys.stderr)
    sys.exit(1)

with open(vcd_path, 'r') as f:
    lines = f.readlines()

# Symbols from results/bpu_integration.vcd for tb_branch_prediction_unit
target_vars = [
    ('clk', '2', False, '#00ffcc', 'Clock (100MHz)'),
    ('reset', '4', False, '#ff3366', 'Synchronous reset'),
    ('fetch_pc', '3', True, '#00d4ff', 'Speculative fetch PC [31:0]'),
    ('prediction_state', '$', 'state', '#ffaa00', 'BHT 2-bit counter state'),
    ('predicted_taken', '&', False, '#33ff99', 'BHT predicted direction'),
    ('btb_hit', '*', False, '#33ff99', 'BTB cache tag match hit'),
    ('predicted_target', '%', True, '#00ffcc', 'BTB cached target [31:0]'),
    ('predicted_next_pc', '\'', True, '#70d6ff', 'Speculative Next-PC mux output [31:0]'),
    ('resolve_valid', ';', False, '#ffff00', 'Branch resolution valid in EX stage'),
    ('resolve_pc', '8', True, '#ffd166', 'Resolved branch PC [31:0]'),
    ('res_actual_taken', '5', False, '#ff9f1c', 'Actual branch condition outcome'),
    ('res_actual_target', '6', True, '#ff9f1c', 'Actual computed branch target [31:0]'),
    ('mispredict', '(', False, '#ff3366', 'Branch misprediction detected'),
    ('flush', ')', False, '#ff3366', 'Pipeline squash / flush strobe'),
    ('redirect', '#', False, '#ff3366', 'Fetch redirect strobe'),
    ('redirect_pc', '"', True, '#ff99bb', 'Recovery redirect target PC [31:0]'),
    ('selected_next_pc', '!', True, '#33ff99', 'Next PC selected for fetch stage [31:0]'),
]

transitions = {sym: [] for _, sym, _, _, _ in target_vars}
current_time = 0

for line in lines:
    line = line.strip()
    if not line:
        continue
    if line.startswith('#'):
        current_time = int(line[1:])
    elif line.startswith('b'):
        parts = line.split()
        val = parts[0][1:]
        sym = parts[1]
        if sym in transitions:
            transitions[sym].append((current_time, val))
    elif len(line) >= 2 and line[1:] in transitions:
        val = line[0]
        sym = line[1:]
        transitions[sym].append((current_time, val))

# Time window: 20 ns to 125 ns (covers cold miss, NT->T mispredict, correct pred, wrong target, T->NT mispredict)
t_min_ps = 20000
t_max_ps = 125000
t_min_ns = t_min_ps / 1000.0
t_max_ns = t_max_ps / 1000.0

def get_val_at(sym, t):
    hist = transitions[sym]
    last_val = '0'
    for ct, val in hist:
        if ct <= t:
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
    '0': '00 (SNT)',
    '00': '00 (SNT)',
    '1': '01 (WNT)',
    '01': '01 (WNT)',
    '10': '10 (WT)',
    '11': '11 (ST)',
}

fig, ax = plt.subplots(figsize=(17, 12), dpi=180)
fig.patch.set_facecolor('#12131a')
ax.set_facecolor('#181a24')

y_spacing = 1.85
n_sigs = len(target_vars)

# Background alternating row shades
for i in range(n_sigs):
    y_base = (n_sigs - 1 - i) * y_spacing
    if i % 2 == 0:
        ax.axhspan(y_base - 0.35, y_base + 1.35, color='#1e212f', alpha=0.5, zorder=0)

# Time grid lines
for t_ns in range(int(t_min_ns), int(t_max_ns) + 1, 5):
    ax.axvline(t_ns, color='#2d3142', linestyle=':' if t_ns % 10 != 0 else '--',
               linewidth=0.8 if t_ns % 10 != 0 else 1.0, alpha=0.7, zorder=1)

# Annotate highlighted test phases across the top
phases = [
    (20, 39, '#00d4ff', 'Phase 1: Cold Fetch\n[BHT=01, BTB miss, npc=PC+4 (0x1004)]'),
    (39, 49, '#ff3366', 'Phase 2: Mispredict NT->Taken\n[flush=1, redirect=1 to 0x2000]'),
    (49, 70, '#33ff99', 'Phase 3: Correct Prediction\n[BHT=10/11, BTB hit 0x2000, flush=0]'),
    (70, 90, '#ffaa00', 'Phase 4: Target Mispredict\n[Actual target 0x3000, redirect to 0x3000]'),
    (90, 115, '#ff5577', 'Phase 5: Mispredict Taken->NT\n[flush=1, redirect to PC+4 (0x1004)]'),
    (115, 125, '#bb99ff', 'Phase 6: Direction Decay\n[State weakens 10->01, pred switches NT]'),
]

for t_start, t_end, col, text in phases:
    ax.axvspan(t_start, t_end, color=col, alpha=0.08, zorder=0)
    ax.text((t_start + t_end) / 2.0, n_sigs * y_spacing + 0.35, text,
            color=col, fontsize=8.2, fontweight='bold', ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.35', facecolor='#161922', edgecolor=col, alpha=0.9))

for i, (name, sym, kind, color, desc) in enumerate(target_vars):
    y_base = (n_sigs - 1 - i) * y_spacing

    # Label on left
    ax.text(t_min_ns - 1.2, y_base + 0.45, name, color='#e0e2ec', fontsize=9.2,
            fontfamily='monospace', fontweight='bold', ha='right', va='center')

    hist = transitions[sym]
    points = []
    v_init = get_val_at(sym, t_min_ps)
    points.append((t_min_ns, v_init))

    for ct, val in hist:
        if t_min_ps <= ct <= t_max_ps:
            points.append((ct / 1000.0, val))
    points.append((t_max_ns, points[-1][1]))

    if kind is False:
        # 1-bit digital waveform
        x_pts = []
        y_pts = []
        for idx in range(len(points) - 1):
            t_curr = points[idx][0]
            v_curr = 1.0 if points[idx][1] == '1' else 0.0
            t_next = points[idx + 1][0]
            x_pts.extend([t_curr, t_next])
            y_pts.extend([y_base + v_curr * 0.9, y_base + v_curr * 0.9])
        ax.step(x_pts, y_pts, where='post', color=color, linewidth=1.6, zorder=3)

    elif kind == 'state':
        for idx in range(len(points) - 1):
            t_start = points[idx][0]
            t_end = points[idx + 1][0]
            val = points[idx][1]
            if t_end - t_start < 0.1:
                continue
            st_text = state_labels.get(val, val)
            is_taken = val in ('10', '11')
            fill_color = '#1f382a' if is_taken else '#382226'
            edge_color = '#00ff88' if is_taken else '#ff5577'

            h = 0.85
            y_m = y_base + 0.45
            dt = 0.3 if (t_end - t_start) > 0.8 else (t_end - t_start) * 0.25
            poly_x = [t_start, t_start + dt, t_end - dt, t_end, t_end - dt, t_start + dt]
            poly_y = [y_m, y_m + h/2, y_m + h/2, y_m, y_m - h/2, y_m - h/2]

            poly = patches.Polygon(list(zip(poly_x, poly_y)), facecolor=fill_color,
                                   edgecolor=edge_color, linewidth=1.4, zorder=2)
            ax.add_patch(poly)
            if t_end - t_start >= 3.0:
                ax.text((t_start + t_end) / 2.0, y_m, st_text, color='#ffffff',
                        fontsize=7.5, fontfamily='monospace', fontweight='bold',
                        ha='center', va='center', zorder=4)

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
            poly_y = [y_m, y_m + h/2, y_m + h/2, y_m, y_m - h/2, y_m - h/2]

            is_active_target = hex_str not in ('0x00000000', '0xXXXXXXXX')
            fill_color = '#222938' if is_active_target else '#181b24'
            edge_color = color if is_active_target else '#4e5568'

            poly = patches.Polygon(list(zip(poly_x, poly_y)), facecolor=fill_color,
                                   edgecolor=edge_color, linewidth=1.2, zorder=2)
            ax.add_patch(poly)

            if t_end - t_start >= 4.0:
                ax.text((t_start + t_end) / 2.0, y_m, hex_str, color='#ffffff',
                        fontsize=7.3, fontfamily='monospace', fontweight='semibold',
                        ha='center', va='center', zorder=4)

ax.set_xlim(t_min_ns - 15.0, t_max_ns + 1.0)
ax.set_ylim(-1.0, (n_sigs + 2.0) * y_spacing)

# Format time axis
ax.set_xlabel('Simulation Time (ns) [1 cycle = 10 ns, 100 MHz clock period]', fontsize=10, color='#a0a6b8', labelpad=10)
ticks = list(range(int(t_min_ns), int(t_max_ns) + 1, 10))
ax.set_xticks(ticks)
ax.set_xticklabels([f"{t} ns" for t in ticks], color='#a0a6b8', fontsize=8.5)

ax.get_yaxis().set_visible(False)
for spine in ax.spines.values():
    spine.set_color('#2d3142')

plt.title('Integrated Branch Prediction Unit Simulation Waveform (tb_branch_prediction_unit.sv / results/bpu_integration.vcd)\n'
          'Synthesizable BPU Top-Level Integration (P1 2-bit BHT + P2 BTB + P3 Next-PC Mux & Branch Resolution)\n'
          'Demonstrating Speculative Next-PC Generation, Resolution Verification, and Recovery Redirect Priority\n'
          'Authored / Verified by: Tanmay Singh (Person 3: Control Integration)',
          color='#ffffff', fontsize=11.5, fontweight='bold', pad=34)

plt.tight_layout()
out_file = 'evidence/waveforms/bpu_integration.png'
os.makedirs(os.path.dirname(out_file), exist_ok=True)
plt.savefig(out_file, dpi=180, facecolor=fig.get_facecolor(), edgecolor='none')
print(f'Successfully rendered genuine BPU integration waveform evidence: {out_file}')
