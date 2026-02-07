"""Unit tests for computeStatistics module."""

# pylint: disable=invalid-name,wrong-import-position

import math
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from p1.source.computeStatistics import (  # type: ignore
    ROW_LABELS,
    build_results_summary,
    compute_dataset_stats,
    compute_mean,
    compute_median,
    compute_mode,
    compute_variance,
    merge_results,
    parse_numbers_from_file,
)


class StatsFunctionsTest(unittest.TestCase):
    """Unit tests for statistics computation helpers."""

    def test_mean_basic(self) -> None:
        """Mean is computed correctly."""

        values = [1.0, 2.0, 3.0, 4.0]
        self.assertAlmostEqual(compute_mean(values), 2.5)

    def test_median_even_and_odd(self) -> None:
        """Median handles even and odd counts."""

        self.assertAlmostEqual(compute_median([1.0, 3.0, 2.0, 4.0]), 2.5)
        self.assertAlmostEqual(compute_median([5.0, 1.0, 3.0]), 3.0)

    def test_mode_multiple_and_none(self) -> None:
        """Mode returns all modes or empty when none."""

        self.assertCountEqual(
            compute_mode([1.0, 2.0, 2.0, 3.0, 3.0]),
            [2.0, 3.0],
        )
        self.assertEqual(compute_mode([4.0, 5.0, 6.0]), [])

    def test_variance_matches_mean(self) -> None:
        """Variance uses provided mean consistently."""

        values = [1.0, 2.0, 3.0]
        mean_value = compute_mean(values)
        variance = compute_variance(values, mean_value)
        self.assertAlmostEqual(mean_value, 2.0)
        self.assertAlmostEqual(variance, 2.0 / 3.0)
        self.assertAlmostEqual(math.sqrt(variance), math.sqrt(2.0 / 3.0))

    def test_parse_numbers_collects_errors(self) -> None:
        """Invalid tokens are reported while parsing numbers."""

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "data.txt"
            file_path.write_text("1 2 a\n3\n", encoding="utf-8")
            numbers, errors = parse_numbers_from_file(file_path)
        self.assertEqual(numbers, [1.0, 2.0, 3.0])
        self.assertEqual(len(errors), 1)
        self.assertIn("Invalid number at line 1", errors[0])
        self.assertIn("a", errors[0])

    def test_build_results_summary_table(self) -> None:
        """Summary renders tabular output for one dataset."""

        numbers = [1.0, 2.0, 3.0]
        stats = compute_dataset_stats(numbers)
        summary = build_results_summary([stats], elapsed_seconds=0.1)
        self.assertEqual(summary[0], "TC\tTC1")
        self.assertEqual(summary[1], "COUNT\t3")
        self.assertEqual(summary[2], "MEAN\t2.00000")
        self.assertEqual(summary[3], "MEDIAN\t2.00000")
        self.assertEqual(summary[4], "MODE\t#N/A")
        self.assertEqual(summary[5], "SD\t0.81650")
        self.assertEqual(summary[6], "VARIANCE\t0.66667")
        self.assertEqual(summary[7], "ELAPSED (s)\t0.10000")

    def test_merge_results_appends_columns(self) -> None:
        """Merge appends new run columns preserving row order."""

        existing = [
            "TC\tTC1",
            "COUNT\t3",
            "MEAN\t2.00000",
            "MEDIAN\t2.00000",
            "MODE\t#N/A",
            "SD\t0.81650",
            "VARIANCE\t0.66667",
            "ELAPSED (s)\t0.10000",
        ]

        new = [
            "TC\tTC1",
            "COUNT\t2",
            "MEAN\t5.00000",
            "MEDIAN\t5.00000",
            "MODE\t5.00000",
            "SD\t0.00000",
            "VARIANCE\t0.00000",
            "ELAPSED (s)\t0.20000",
        ]

        merged = merge_results(existing, new)

        self.assertEqual(merged[0], "TC\tTC1\tTC2")
        rows = {
            line.split("\t", maxsplit=1)[0]: line
            for line in merged[1:]
        }
        self.assertEqual(rows["COUNT"], "COUNT\t3\t2")
        self.assertEqual(rows["MEAN"], "MEAN\t2.00000\t5.00000")
        self.assertEqual(rows["MODE"], "MODE\t#N/A\t5.00000")
        self.assertEqual(rows["ELAPSED (s)"], "ELAPSED (s)\t0.10000\t0.20000")

        # Ensure all expected labels are present.
        self.assertEqual(set(rows.keys()), set(ROW_LABELS))


if __name__ == "__main__":
    unittest.main()
