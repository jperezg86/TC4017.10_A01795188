"""CLI tool to compute sales totals from JSON inputs."""

from __future__ import annotations

import argparse
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


def main() -> int:
    """Program entrypoint."""
    parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
