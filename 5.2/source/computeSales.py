"""CLI tool to compute sales totals from JSON inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def load_json(file_path: Path):
    """Load JSON content from the given file path."""
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_price_lookup(price_catalogue: list[dict]) -> dict[str, float]:
    """Build a price lookup map from title to price."""
    lookup: dict[str, float] = {}
    for product in price_catalogue:
        title = str(product["title"])
        lookup[title] = float(product["price"])
    return lookup


def compute_item_cost(item: str | dict, lookup: dict[str, float]) -> float:
    """Compute cost for a single item entry."""
    if isinstance(item, str):
        return lookup[item]

    title = str(item["title"])
    quantity = int(item.get("quantity", 1))
    return lookup[title] * quantity


def compute_sales_totals(
    sales_records: list[dict],
    lookup: dict[str, float],
) -> tuple[list[float], float]:
    """Compute per-sale totals and global total."""
    sale_totals: list[float] = []
    global_total = 0.0

    for sale in sales_records:
        sale_total = 0.0
        for item in sale["items"]:
            sale_total += compute_item_cost(item, lookup)
        sale_totals.append(sale_total)
        global_total += sale_total

    return sale_totals, global_total


def format_results(sale_totals: list[float], global_total: float) -> str:
    """Build a human-readable result string."""
    lines = ["Sales Summary", "=" * 40]
    for index, value in enumerate(sale_totals, start=1):
        lines.append(f"Sale #{index:04d}: ${value:.2f}")
    lines.append("-" * 40)
    lines.append(f"Grand Total: ${global_total:.2f}")
    return "\n".join(lines)


def main() -> int:
    """Program entrypoint."""
    args = parse_args()

    price_catalogue = load_json(args.price_catalogue)
    sales_records = load_json(args.sales_record)

    lookup = build_price_lookup(price_catalogue)
    sale_totals, global_total = compute_sales_totals(sales_records, lookup)

    print(format_results(sale_totals, global_total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
