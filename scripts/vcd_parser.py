#!/usr/bin/env python3
"""
vcd_parser.py
Shared strict VCD header and value-change parser for waveform rendering scripts.
"""

import re

UNIT_MULTIPLIERS_NS = {
    "s": 1e9,
    "ms": 1e6,
    "us": 1e3,
    "ns": 1.0,
    "ps": 1e-3,
    "fs": 1e-6,
}


def _iter_header_blocks(handle):
    """Yield (keyword, tokens) pairs from a VCD header up to $enddefinitions."""
    current_kw = None
    current_tokens = []
    for raw_line in handle:
        for tok in raw_line.split():
            if current_kw is None:
                if not tok.startswith("$"):
                    raise ValueError(
                        f"Unexpected VCD header token outside declaration: {tok!r}"
                    )
                current_kw = tok
                current_tokens = []
            elif tok == "$end":
                yield current_kw, current_tokens
                if current_kw == "$enddefinitions":
                    return
                current_kw = None
                current_tokens = []
            else:
                current_tokens.append(tok)
    if current_kw is not None:
        raise ValueError(f"Unterminated VCD header declaration: {current_kw}")


def parse_timescale(tokens):
    """Validate and convert VCD $timescale tokens into (canonical_str, ns_float)."""
    raw = " ".join(tokens).strip()
    if not raw:
        raise ValueError("Empty $timescale declaration in VCD header")
    match = re.fullmatch(r"(1|10|100)\s*(s|ms|us|ns|ps|fs)", raw)
    if not match:
        raise ValueError(
            f"Invalid VCD $timescale declaration {raw!r}; "
            "expected magnitude 1|10|100 with unit s|ms|us|ns|ps|fs"
        )
    magnitude = int(match.group(1))
    unit = match.group(2)
    return f"{magnitude}{unit}", magnitude * UNIT_MULTIPLIERS_NS[unit]


def parse_vcd_header(vcd_path, target_scope, required_signals):
    """Parse VCD header strictly and resolve required_signals within target_scope.

    Supports both single-line ('$timescale 1ps $end') and multi-line declarations.
    Raises ValueError if $timescale is missing/invalid/duplicate, if $enddefinitions
    is missing, or if any required signal is missing or ambiguous in target_scope.
    """
    scope_stack = []
    signals = {}
    timescale_info = None
    saw_enddefinitions = False

    with open(vcd_path, "r", encoding="utf-8", errors="replace") as f:
        for kw, tokens in _iter_header_blocks(f):
            if kw == "$timescale":
                if timescale_info is not None:
                    raise ValueError("Duplicate $timescale declaration in VCD header")
                timescale_info = parse_timescale(tokens)
            elif kw == "$scope":
                if len(tokens) < 2:
                    raise ValueError(f"Malformed $scope declaration: {tokens!r}")
                scope_stack.append(tokens[1])
            elif kw == "$upscope":
                if not scope_stack:
                    raise ValueError("Unmatched $upscope in VCD header")
                scope_stack.pop()
            elif kw == "$var":
                if len(tokens) < 4:
                    raise ValueError(f"Malformed $var declaration: {tokens!r}")
                try:
                    size = int(tokens[1])
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid bit width in $var declaration: {tokens!r}"
                    ) from exc
                if size <= 0:
                    raise ValueError(
                        f"Non-positive bit width in $var declaration: {tokens!r}"
                    )
                sym = tokens[2]
                var_name = tokens[3]
                curr_scope = ".".join(scope_stack)
                signals.setdefault((curr_scope, var_name), []).append((sym, size))
            elif kw == "$enddefinitions":
                saw_enddefinitions = True
                break

    if not saw_enddefinitions:
        raise ValueError(f"Missing $enddefinitions in VCD header: {vcd_path}")
    if timescale_info is None:
        raise ValueError(f"Missing $timescale declaration in VCD header: {vcd_path}")

    resolved = {}
    missing = []
    for sig_name in required_signals:
        entries = signals.get((target_scope, sig_name))
        if not entries:
            missing.append(sig_name)
        elif len(entries) > 1:
            raise ValueError(
                f"Ambiguous VCD signal declaration for '{sig_name}' in scope "
                f"'{target_scope}' ({len(entries)} declarations)"
            )
        else:
            resolved[sig_name] = entries[0]

    if missing:
        raise ValueError(
            f"VCD parsing error: Missing required signals in scope '{target_scope}': {missing}"
        )

    timescale_str, timescale_ns = timescale_info
    return timescale_str, timescale_ns, resolved


def parse_vcd_transitions(vcd_path, symbol_map):
    """Parse value transitions for symbols in symbol_map.

    Returns dict mapping symbol -> list of (raw_timestamp, value).
    """
    tracked_symbols = set(symbol_map.values())
    transitions = {sym: [] for sym in tracked_symbols}
    current_time = 0

    with open(vcd_path, "r", encoding="utf-8", errors="replace") as f:
        saw_enddefinitions = False
        for kw, _ in _iter_header_blocks(f):
            if kw == "$enddefinitions":
                saw_enddefinitions = True
                break
        if not saw_enddefinitions:
            raise ValueError(f"Missing $enddefinitions in VCD file: {vcd_path}")

        for line in f:
            line = line.strip()
            if not line or line.startswith("$"):
                continue
            if line.startswith("#"):
                current_time = int(line[1:])
            elif line[0] in ("b", "B", "r", "R"):
                parts = line.split()
                if len(parts) >= 2:
                    val = parts[0][1:]
                    sym = parts[1]
                    if sym in transitions:
                        transitions[sym].append((current_time, val))
            elif len(line) >= 2 and line[1:] in transitions:
                val = line[0]
                sym = line[1:]
                transitions[sym].append((current_time, val))

    return transitions
