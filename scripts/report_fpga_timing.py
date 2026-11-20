#!/usr/bin/env python3
"""Extract an evidenced post-route iCE40 Fmax estimate; never guess the MHz value.

The netlist must contain real mapped FPGA primitives, and the log must
contain a routed-clock frequency as printed by nextpnr. Outputs remain
generated artifacts until reviewed/committed separately.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

RTL_PATHS = (
    "rtl/branch_history_table.v",
    "rtl/predictor_2bit.v",
    "rtl/branch_target_buffer.v",
    "rtl/next_pc_mux.v",
    "rtl/branch_resolution.v",
    "rtl/branch_prediction_unit.v",
    "rtl/fpga_timing_harness.v",
)
CLOCK_REGEX = re.compile(
    r"Max frequency for clock ['\"]([^'\"]+)['\"]:\s*([0-9]+(?:\.[0-9]+)?)\s*MHz"
    r"(?:\s*\((PASS|FAIL) at ([0-9]+(?:\.[0-9]+)?)\s*MHz\))?",
    re.IGNORECASE,
)


def build_summary(netlist: Path, log: Path, asc: Path, tools: Path) -> dict:
    if not asc.is_file() or asc.stat().st_size == 0:
        raise ValueError("No routed ASC file; cannot claim post-route timing")
    data = json.loads(netlist.read_text())
    top = data.get("modules", {}).get("bpu_fpga_timing_top")
    if not top:
        raise ValueError("Mapped timing top missing from Yosys JSON")
    kinds = collections.Counter(c.get("type", "") for c in top.get("cells", {}).values())
    lut = kinds.get("SB_LUT4", 0)
    ff = sum(n for t, n in kinds.items() if t.startswith("SB_DFF"))
    if lut < 200 or ff < 100:
        raise ValueError(
            f"Potentially optimized-away design: {lut} iCE40 LUTs / {ff} FFs"
        )
    if any(not (t.startswith("SB_") or t.startswith("\\$")) for t in kinds):
        raise ValueError("Unexpected unmapped cell types: " + str(kinds))
    port_count = sum(len(p.get("bits", [])) for p in top.get("ports", {}).values())
    if port_count > 206:
        raise ValueError(f"HX8K-CT256 port budget exceeded: {port_count} bits")

    log_text = log.read_text(errors="replace")
    found = list(CLOCK_REGEX.finditer(log_text))
    if not found:
        raise ValueError("nextpnr reported no routed Fmax; refusing synthetic MHz")
    last = found[-1]
    mhz = float(last.group(2))
    if mhz <= 0:
        raise ValueError("Non-positive Fmax")
    # nextpnr logs placement- and route-stage Fmax; the *last* logged
    # frequency is taken only if a routed output file has been produced.
    status = last.group(3)
    target_mhz = float(last.group(4)) if last.group(4) else None
    if "ERROR:" in log_text or "ERROR: " in log_text:
        raise ValueError("nextpnr error present in routing log")
    source_hashes = {
        path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
        for path in RTL_PATHS
    }
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = os.environ.get("GITHUB_SHA", "unknown")

    return {
        "metric": "registered-harness post-route clock Fmax estimate",
        "is_physical_measurement": False,
        "device": "Lattice iCE40HX8K",
        "package": "CT256",
        "top": "bpu_fpga_timing_top",
        "base_module": "rtl/branch_prediction_unit.v",
        "clock": last.group(1),
        "fmax_estimate_mhz": round(mhz, 2),
        "estimated_min_period_ns": round(1000.0 / mhz, 2),
        "requested_clock_mhz": target_mhz,
        "met_requested_clock_goal": status == "PASS" if status else None,
        "post_route_file": str(asc),
        "mapped_lut4": lut,
        "mapped_flip_flops": ff,
        "mapped_carry": kinds.get("SB_CARRY", 0),
        "mapped_ram40": sum(n for t, n in kinds.items() if t.startswith("SB_RAM40")),
        "mapped_cell_types": dict(sorted(kinds.items())),
        "io_port_bits": port_count,
        "git_commit": commit,
        "source_sha256": source_hashes,
        "tool_versions": tools.read_text().strip() if tools.is_file() else "See CI log",
        "caveats": [
            "Software place-and-route timing estimate for a registered BPU test harness, not a measured board Fmax.",
            "No physical FPGA board, pin mapping/PCF, input/output arrival/loading, or external timing constraints were specified.",
            "Register-to-register synchronous clock paths are evaluated; not every system timing path is constrained.",
            "The harness adds input/output registers; its timing is not identical to an in-CPU deployment of the BPU.",
            "The original BPU RTL remains unchanged. No CPU application speedup or actual FPGA MHz was measured.",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--netlist", type=Path, required=True)
    p.add_argument("--log", type=Path, required=True)
    p.add_argument("--asc", type=Path, required=True)
    p.add_argument("--tools", type=Path, required=True)
    p.add_argument("--json-out", type=Path, required=True)
    p.add_argument("--markdown-out", type=Path, required=True)
    a = p.parse_args()
    summary = build_summary(a.netlist, a.log, a.asc, a.tools)
    a.json_out.parent.mkdir(parents=True, exist_ok=True)
    a.json_out.write_text(json.dumps(summary, indent=2) + "\n")
    achieved = summary["met_requested_clock_goal"]
    goal = ("met" if achieved else "not met") if achieved is not None else "not reported"
    md = f"""# FPGA timing study — software-estimated post-route results

| Item | Result |
| --- | --- |
| Target | {summary['device']}-{summary['package']} (no physical board) |
| Synthesized top | `{summary['top']}` (existing BPU + registered I/O) |
| Estimated post-route Fmax | **{summary['fmax_estimate_mhz']:.2f} MHz** |
| Estimated minimum period | {summary['estimated_min_period_ns']:.2f} ns |
| Requested timing goal | {summary['requested_clock_mhz']} MHz ({goal}) |
| Mapped SB_LUT4 | {summary['mapped_lut4']} |
| Mapped flip-flops | {summary['mapped_flip_flops']} |
| Mapped SB_CARRY | {summary['mapped_carry']} |
| Mapped RAM blocks | {summary['mapped_ram40']} |
| External port bits | {summary['io_port_bits']} |
| Source commit | `{summary['git_commit']}` |

## Tool versions

```
{summary['tool_versions']}
```

## Limits and exact scope

""" + "".join(f"- {c}\n" for c in summary["caveats"]) + """
The MHz figure was parsed from nextpnr's **last** reported clock-frequency result
after it successfully created the routed `.asc` file. The tool's raw routing
and timing log is retained in the workflow artifact and should be consulted
for the limiting path and warnings. A supervisor must decide whether this
target-independent study is adequate for the course Fmax requirement.
"""
    a.markdown_out.write_text(md)
    print(a.markdown_out.read_text())


if __name__ == "__main__":
    main()
