"""Verify strict VCD timescale, scope/signal resolution, and transition parsing."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vcd_parser", ROOT / "scripts/vcd_parser.py")
vcd_parser = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vcd_parser)


class VcdParserTests(unittest.TestCase):
    def _write_temp_vcd(self, directory, content):
        path = Path(directory) / "sample.vcd"
        path.write_text(content, encoding="utf-8")
        return path

    def test_parses_single_line_timescale_and_resolves_signals(self):
        vcd = """\
$date today $end
$timescale 1ps $end
$scope module tb $end
$var wire 1 ! clk $end
$var reg 32 " pc [31:0] $end
$upscope $end
$enddefinitions $end
#0
0!
b00000000000000000000000000010000 "
#5000
1!
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            ts_str, ts_ns, resolved = vcd_parser.parse_vcd_header(
                path, "tb", ["clk", "pc"]
            )
            self.assertEqual(ts_str, "1ps")
            self.assertAlmostEqual(ts_ns, 1e-3, places=9)
            self.assertEqual(resolved, {"clk": ("!", 1), "pc": ('"', 32)})

            transitions = vcd_parser.parse_vcd_transitions(
                path, {"clk": "!", "pc": '"'}
            )
            self.assertEqual(transitions["!"], [(0, "0"), (5000, "1")])
            self.assertEqual(
                transitions['"'], [(0, "00000000000000000000000000010000")]
            )

    def test_parses_single_line_timescale_with_space(self):
        vcd = """\
$timescale 100 us $end
$scope module tb $end
$var wire 1 ! clk $end
$upscope $end
$enddefinitions $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            ts_str, ts_ns, resolved = vcd_parser.parse_vcd_header(path, "tb", ["clk"])
            self.assertEqual(ts_str, "100us")
            self.assertAlmostEqual(ts_ns, 1e5, places=6)
            self.assertEqual(resolved["clk"], ("!", 1))

    def test_parses_multiline_timescale(self):
        vcd = """\
$timescale
    10ns
$end
$scope module tb $end
$var wire 1 ! clk $end
$upscope $end
$enddefinitions $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            ts_str, ts_ns, _ = vcd_parser.parse_vcd_header(path, "tb", ["clk"])
            self.assertEqual(ts_str, "10ns")
            self.assertAlmostEqual(ts_ns, 10.0, places=9)

    def test_rejects_missing_timescale(self):
        vcd = """\
$date today $end
$scope module tb $end
$var wire 1 ! clk $end
$upscope $end
$enddefinitions $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            with self.assertRaisesRegex(ValueError, "Missing \\$timescale"):
                vcd_parser.parse_vcd_header(path, "tb", ["clk"])

    def test_rejects_invalid_timescales(self):
        invalid_blocks = [
            "$timescale $end",
            "$timescale 0ps $end",
            "$timescale 5ns $end",
            "$timescale 1000ps $end",
            "$timescale -1ns $end",
            "$timescale 1ks $end",
            "$timescale 1NS $end",
            "$timescale 1ps extra $end",
            "$timescale\n  25ps\n$end",
        ]
        for block in invalid_blocks:
            vcd = f"""\
{block}
$scope module tb $end
$var wire 1 ! clk $end
$upscope $end
$enddefinitions $end
"""
            with self.subTest(block=block):
                with tempfile.TemporaryDirectory() as tmp:
                    path = self._write_temp_vcd(tmp, vcd)
                    with self.assertRaises(ValueError):
                        vcd_parser.parse_vcd_header(path, "tb", ["clk"])

    def test_rejects_unterminated_timescale(self):
        vcd = """\
$timescale 1ps
$scope module tb $end
$var wire 1 ! clk $end
$upscope $end
$enddefinitions $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            with self.assertRaises(ValueError):
                vcd_parser.parse_vcd_header(path, "tb", ["clk"])

    def test_rejects_duplicate_timescale(self):
        vcd = """\
$timescale 1ps $end
$timescale 1ns $end
$scope module tb $end
$var wire 1 ! clk $end
$upscope $end
$enddefinitions $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            with self.assertRaisesRegex(ValueError, "Duplicate \\$timescale"):
                vcd_parser.parse_vcd_header(path, "tb", ["clk"])

    def test_rejects_missing_signal_or_scope(self):
        vcd = """\
$timescale 1ps $end
$scope module tb $end
$var wire 1 ! clk $end
$upscope $end
$enddefinitions $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            with self.assertRaisesRegex(ValueError, "Missing required signals"):
                vcd_parser.parse_vcd_header(path, "tb", ["clk", "reset"])
            with self.assertRaisesRegex(ValueError, "Missing required signals"):
                vcd_parser.parse_vcd_header(path, "other_tb", ["clk"])

    def test_rejects_ambiguous_duplicate_signal_in_same_scope(self):
        vcd = """\
$timescale 1ps $end
$scope module tb $end
$var wire 1 ! clk $end
$var reg 1 " clk $end
$upscope $end
$enddefinitions $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            with self.assertRaisesRegex(ValueError, "Ambiguous"):
                vcd_parser.parse_vcd_header(path, "tb", ["clk"])

    def test_distinguishes_same_signal_name_across_scopes(self):
        vcd = """\
$timescale 1ps $end
$scope module tb $end
$var wire 1 ! clk $end
$scope module dut $end
$var wire 1 " clk $end
$upscope $end
$upscope $end
$enddefinitions $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            _, _, resolved = vcd_parser.parse_vcd_header(path, "tb", ["clk"])
            self.assertEqual(resolved["clk"], ("!", 1))

    def test_rejects_missing_enddefinitions(self):
        vcd = """\
$timescale 1ps $end
$scope module tb $end
$var wire 1 ! clk $end
$upscope $end
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_temp_vcd(tmp, vcd)
            with self.assertRaisesRegex(ValueError, "Missing \\$enddefinitions"):
                vcd_parser.parse_vcd_header(path, "tb", ["clk"])


if __name__ == "__main__":
    unittest.main()
