"""Regression tests for routed-timing evidence parser, no FPGA tool required."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from report_fpga_timing import build_summary  # noqa: E402


class TestFpgaTimingReport(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.net = root / "synth.json"
        self.log = root / "route.log"
        self.asc = root / "route.asc"
        self.tools = root / "versions.txt"
        self.net.write_text(json.dumps({
            "modules": {
                "bpu_fpga_timing_top": {
                    "cells": {
                        **{f"LUT{i}": {"type": "SB_LUT4"} for i in range(300)},
                        **{f"DFF{i}": {"type": "SB_DFF"} for i in range(200)},
                    },
                    "ports": {
                        "clk": {"bits": [2]},
                        "reset": {"bits": [3]},
                        "observed_pc": {"bits": list(range(40, 72))},
                    },
                }
            }
        }))
        self.log.write_text(
            "Info: Max frequency for clock 'clk': 88.00 MHz (PASS at 25.00 MHz)\n"
            "Info: Routing complete.\n"
            "Info: Max frequency for clock 'clk': 55.50 MHz (PASS at 25.00 MHz)\n"
        )
        self.asc.write_text("routed fixture\n")
        self.tools.write_text("Yosys version fixture\nnextpnr fixture\n")

    def test_uses_last_post_route_frequency(self):
        result = build_summary(self.net, self.log, self.asc, self.tools)
        self.assertEqual(result["fmax_estimate_mhz"], 55.50)
        self.assertEqual(result["estimated_min_period_ns"], 18.02)
        self.assertTrue(result["met_requested_clock_goal"])
        self.assertEqual(result["mapped_lut4"], 300)
        self.assertEqual(result["mapped_flip_flops"], 200)
        self.assertFalse(result["is_physical_measurement"])

    def test_missing_route_cannot_claim_fmax(self):
        self.asc.unlink()
        with self.assertRaisesRegex(ValueError, "No routed ASC"):
            build_summary(self.net, self.log, self.asc, self.tools)

    def test_no_reported_frequency_fails_closed(self):
        self.log.write_text("Info: Routing complete; no clock timing produced\n")
        with self.assertRaisesRegex(ValueError, "no routed Fmax"):
            build_summary(self.net, self.log, self.asc, self.tools)

    def test_optimized_away_design_fails(self):
        self.net.write_text('{"modules":{"bpu_fpga_timing_top":{"cells":{},"ports":{}}}}')
        with self.assertRaisesRegex(ValueError, "optimized-away"):
            build_summary(self.net, self.log, self.asc, self.tools)

    def test_fail_at_requested_goal_reported(self):
        self.log.write_text(
            "Info: Routing complete.\n"
            "Info: Max frequency for clock 'clk': 18.25 MHz (FAIL at 25.00 MHz)\n"
        )
        result = build_summary(self.net, self.log, self.asc, self.tools)
        self.assertFalse(result["met_requested_clock_goal"])
        self.assertEqual(result["fmax_estimate_mhz"], 18.25)


if __name__ == "__main__":
    unittest.main()
