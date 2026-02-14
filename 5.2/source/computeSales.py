"""CLI tool to compute sales totals from JSON inputs."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

RESULT_FILE = Path("SalesResults.txt")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Compute total sales cost from a price catalogue and sales "
            "record JSON files."
        )
    )
    parser.add_argument(
        "price_catalogue",
        type=Path,
        help="Path to the JSON price catalogue file",
    )
    parser.add_argument(
        "sales_record",
        type=Path,
        help="Path to the JSON sales record file",
    )
    return parser.parse_args()


def print_error(message: str) -> None:
    """Print an error message with consistent formatting."""
    print(f"ERROR: {message}")


def load_json(file_path: Path) -> list[Any]:
    """Load a JSON array from a file. Return an empty list on errors."""
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print_error(f"File not found: {file_path}")
        return []
    except json.JSONDecodeError as exc:
        print_error(f"Invalid JSON in {file_path}: {exc}")
        return []

    if not isinstance(data, list):
        print_error(f"Expected JSON array in {file_path}")
        return []

    return data


def build_price_lookup(price_catalogue: list[Any]) -> dict[str, float]:
    """Build a price lookup map from product title to price."""
    lookup: dict[str, float] = {}

    for index, product in enumerate(price_catalogue, start=1):
        if not isinstance(product, dict):
            print_error(
                f"Catalogue row {index}: expected object, got "
                f"{type(product).__name__}"
            )
            continue

        title = product.get("title")
        price = product.get("price")

        if not isinstance(title, str) or not title.strip():
            print_error(f"Catalogue row {index}: invalid or empty title")
            continue

        try:
            price_value = float(price)
        except (TypeError, ValueError):
            print_error(
                f"Catalogue row {index}: invalid price for '{title}': {price}"
            )
            continue

        lookup[title.strip()] = price_value

    return lookup


def normalize_sale_items(
    sale: Any,
    sale_index: int,
) -> list[Any]:
    """Extract sale items while validating the sale structure."""
    if not isinstance(sale, dict):
        print_error(
            f"Sale row {sale_index}: expected object, got "
            f"{type(sale).__name__}"
        )
        return []

    items = sale.get("items")
    if not isinstance(items, list):
        print_error(f"Sale row {sale_index}: 'items' must be a list")
        return []

    return items


def compute_item_cost(
    item: Any,
    lookup: dict[str, float],
    sale_index: int,
    item_index: int,
) -> float:
    """Compute cost for one sale item, returning 0.0 on invalid data."""
    title = ""
    quantity = 1

    if isinstance(item, str):
        title = item.strip()
    elif isinstance(item, dict):
        raw_title = item.get("title")
        if not isinstance(raw_title, str) or not raw_title.strip():
            print_error(
                f"Sale {sale_index}, item {item_index}: invalid title"
            )
            return 0.0
        title = raw_title.strip()

        raw_quantity = item.get("quantity", 1)
        try:
            quantity = int(raw_quantity)
        except (TypeError, ValueError):
            print_error(
                f"Sale {sale_index}, item {item_index}: invalid quantity "
                f"for '{title}': {raw_quantity}"
            )
            return 0.0

        if quantity < 0:
            print_error(
                f"Sale {sale_index}, item {item_index}: quantity cannot "
                f"be negative for '{title}'"
            )
            return 0.0
    else:
        print_error(
            f"Sale {sale_index}, item {item_index}: unsupported item type "
            f"{type(item).__name__}"
        )
        return 0.0

    if title not in lookup:
        print_error(
            f"Sale {sale_index}, item {item_index}: unknown product '{title}'"
        )
        return 0.0

    return lookup[title] * quantity


def compute_sales_totals(
    sales_records: list[Any],
    lookup: dict[str, float],
) -> tuple[list[float], float]:
    """Compute per-sale totals and global total."""
    sale_totals: list[float] = []
    global_total = 0.0

    for sale_index, sale in enumerate(sales_records, start=1):
        items = normalize_sale_items(sale, sale_index)
        sale_total = 0.0

        for item_index, item in enumerate(items, start=1):
            sale_total += compute_item_cost(item, lookup, sale_index, item_index)

        sale_totals.append(sale_total)
        global_total += sale_total

    return sale_totals, global_total


def format_results(
    sale_totals: list[float],
    global_total: float,
    elapsed_seconds: float,
) -> str:
    """Build a human-readable result string."""
    lines = ["Sales Summary", "=" * 40]
    for index, value in enumerate(sale_totals, start=1):
        lines.append(f"Sale #{index:04d}: ${value:.2f}")
    lines.append("-" * 40)
    lines.append(f"Grand Total: ${global_total:.2f}")
    lines.append(f"Elapsed time: {elapsed_seconds:.6f} seconds")
    return "\n".join(lines)


def write_results(content: str, output_file: Path = RESULT_FILE) -> None:
    """Write result content to a text file."""
    output_file.write_text(content + "\n", encoding="utf-8")


def main() -> int:
    """Program entrypoint."""
    start_time = time.perf_counter()
    args = parse_args()

    price_catalogue = load_json(args.price_catalogue)
    sales_records = load_json(args.sales_record)

    lookup = build_price_lookup(price_catalogue)
    sale_totals, global_total = compute_sales_totals(sales_records, lookup)

    elapsed_seconds = time.perf_counter() - start_time
    results_text = format_results(sale_totals, global_total, elapsed_seconds)

    print(results_text)
    write_results(results_text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
