"""Command-line tool to compute descriptive statistics from data files."""

# pylint: disable=invalid-name

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path
from typing import Iterable, List, Tuple

ROW_LABELS = [
    "COUNT",
    "MEAN",
    "MEDIAN",
    "MODE",
    "SD",
    "VARIANCE",
    "ELAPSED (s)",
]


def parse_numbers_from_file(file_path: Path) -> Tuple[List[float], List[str]]:
    """Parse numbers from a text file, collecting any conversion errors."""

    numbers: List[float] = []
    errors: List[str] = []

    with file_path.open("r", encoding="utf-8") as file:
        for line_no, line in enumerate(file, start=1):
            for raw_item in line.strip().split():
                if not raw_item:
                    continue
                try:
                    numbers.append(float(raw_item))
                except ValueError:
                    message = (
                        f"{file_path.name}: Invalid number at line {line_no}: "
                        f"{raw_item}"
                    )
                    errors.append(message)

    return numbers, errors


def compute_dataset_stats(values: List[float]) -> dict:
    """Compute statistics for a single dataset."""

    mean_value = compute_mean(values)
    median_value = compute_median(values)
    modes = compute_mode(values)
    variance_value = compute_variance(values, mean_value)
    std_dev_value = math.sqrt(variance_value)

    return {
        "count": len(values),
        "mean": mean_value,
        "median": median_value,
        "modes": modes,
        "variance": variance_value,
        "std_dev": std_dev_value,
    }


def compute_mean(values: Iterable[float]) -> float:
    """Return the arithmetic mean of the provided values."""

    total = 0.0
    count = 0
    for value in values:
        total += value
        count += 1
    if count == 0:
        raise ValueError("Cannot compute mean of an empty sequence")
    return total / count


def compute_median(values: List[float]) -> float:
    """Return the median of the provided values."""

    if not values:
        raise ValueError("Cannot compute median of an empty sequence")

    sorted_values = sorted(values)
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2 == 0:
        return (sorted_values[mid - 1] + sorted_values[mid]) / 2
    return sorted_values[mid]


def compute_mode(values: Iterable[float]) -> List[float]:
    """Return a list of modes, or an empty list when all frequencies are 1."""

    frequency = {}
    for value in values:
        frequency[value] = frequency.get(value, 0) + 1

    if not frequency:
        raise ValueError("Cannot compute mode of an empty sequence")

    max_frequency = max(frequency.values())
    if max_frequency == 1:
        return []
    # Multiple items can share the highest frequency.
    return [
        value
        for value, count in frequency.items()
        if count == max_frequency
    ]


def compute_variance(values: Iterable[float], mean: float) -> float:
    """Return the population variance for the provided values and mean."""

    total = 0.0
    count = 0
    for value in values:
        diff = value - mean
        total += diff * diff
        count += 1
    if count == 0:
        raise ValueError("Cannot compute variance of an empty sequence")
    return total / count


def format_number(value: float) -> str:
    """Format a float to five decimal places."""
    return f"{value:.5f}"


def format_modes(modes: List[float]) -> str:
    """Format modes returning a single representative value or #N/A."""
    if not modes:
        return "#N/A"
    # User preference: when multiple modes tie, show only the maximum.
    return format_number(max(modes))


def write_results(output_path: Path, results: List[str]) -> None:
    """Persist the computed results to the output file path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(results) + "\n", encoding="utf-8")


def pad_or_trim(values: List[str], expected: int) -> List[str]:
    """Ensure the list has the expected length, padding with #N/A if needed."""

    if len(values) < expected:
        values = values + ["#N/A"] * (expected - len(values))
    elif len(values) > expected:
        values = values[:expected]
    return values


def parse_table(lines: List[str]) -> dict:
    """Convert TSV lines into a label-to-values mapping."""

    mapping = {}
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) >= 2:
            mapping[parts[0]] = parts[1:]
    return mapping


def merge_results(
    existing_lines: List[str],
    new_lines: List[str],
) -> List[str]:
    """Merge new result columns into existing TSV results."""

    if not existing_lines:
        return new_lines

    existing_headers = existing_lines[0].split("\t")
    existing_cols = len(existing_headers) - 1
    new_cols = len(new_lines[0].split("\t")) - 1

    total_cols = existing_cols + new_cols
    headers = ["TC"] + [f"TC{i}" for i in range(1, total_cols + 1)]

    existing_map = parse_table(existing_lines)
    new_map = parse_table(new_lines)

    merged_lines = ["\t".join(headers)]

    for label in ROW_LABELS:
        existing_vals = pad_or_trim(
            existing_map.get(label, ["#N/A"] * existing_cols),
            existing_cols,
        )
        new_vals = pad_or_trim(
            new_map.get(label, ["#N/A"] * new_cols),
            new_cols,
        )
        merged_lines.append("\t".join([label] + existing_vals + new_vals))

    return merged_lines


def build_results_summary(
    datasets: List[dict | None],
    elapsed_seconds: float,
) -> List[str]:
    """Build a tab-separated report for multiple datasets."""

    headers = ["TC"] + [f"TC{idx}" for idx in range(1, len(datasets) + 1)]
    lines = ["\t".join(headers)]

    def format_row(label: str, extractor) -> str:
        row = [label]
        for stats in datasets:
            if stats is None:
                row.append("#N/A")
                continue
            value = extractor(stats)
            if label == "MODE":
                row.append(format_modes(value))
            elif label == "COUNT":
                row.append(str(value))
            else:
                row.append(format_number(value))
        return "\t".join(row)

    lines.append(format_row("COUNT", lambda s: s["count"]))
    lines.append(format_row("MEAN", lambda s: s["mean"]))
    lines.append(format_row("MEDIAN", lambda s: s["median"]))
    lines.append(format_row("MODE", lambda s: s["modes"]))
    lines.append(format_row("SD", lambda s: s["std_dev"]))
    lines.append(format_row("VARIANCE", lambda s: s["variance"]))
    # Elapsed time is global for the run; repeat for each column for clarity.
    elapsed_row = ["ELAPSED (s)"] + [
        format_number(elapsed_seconds)
        for _ in datasets
    ]
    lines.append("\t".join(elapsed_row))

    return lines


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Compute mean, median, mode, variance, and standard deviation for "
            "numbers listed in a file."
        )
    )
    parser.add_argument(
        "data_files",
        nargs="+",
        type=Path,
        help="One or more paths to input files containing numeric values",
    )
    return parser.parse_args()


def main() -> int:  # pylint: disable=too-many-locals
    """Entry point for the CLI tool."""
    args = parse_args()
    start_time = time.perf_counter()

    datasets: List[dict | None] = []
    errors: List[str] = []

    for path in args.data_files:
        if not path.is_file():
            errors.append(f"Input file not found: {path}")
            datasets.append(None)
            continue

        numbers, file_errors = parse_numbers_from_file(path)
        errors.extend(file_errors)

        if not numbers:
            errors.append(
                f"{path.name}: No valid numeric data found. Skipping."
            )
            datasets.append(None)
            continue

        stats = compute_dataset_stats(numbers)
        datasets.append(stats)

    for error in errors:
        print(error, file=sys.stderr)

    if all(dataset is None for dataset in datasets):
        message = (
            "No valid numeric data found in any provided file. "
            "Nothing to compute."
        )
        print(message, file=sys.stderr)
        return 1

    elapsed_seconds = time.perf_counter() - start_time

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "results" / "StatisticsResults.txt"

    run_summary = build_results_summary(datasets, elapsed_seconds)

    merged_summary = run_summary
    if output_path.exists():
        existing_lines = output_path.read_text(encoding="utf-8").splitlines()
        merged_summary = merge_results(existing_lines, run_summary)

    write_results(output_path, merged_summary)

    for line in run_summary:
        print(line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
