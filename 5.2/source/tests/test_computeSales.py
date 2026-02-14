"""Tests for computeSales CLI and helpers."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


MODULE_PATH = Path("5.2/source/computeSales.py")


def load_module():
    """Load computeSales module directly from its file path."""
    spec = importlib.util.spec_from_file_location("computeSales", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload) -> None:
    """Write JSON payload to file."""
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_compute_sales_totals_with_mixed_items() -> None:
    """It computes totals for string and object item entries."""
    compute_sales = load_module()

    catalogue = [
        {"title": "apple", "price": 2.5},
        {"title": "banana", "price": 1.0},
    ]
    sales = [
        {"items": ["apple", {"title": "banana", "quantity": 3}]},
        {"items": [{"title": "apple", "quantity": 2}]},
    ]

    lookup = compute_sales.build_price_lookup(catalogue)
    sale_totals, global_total = compute_sales.compute_sales_totals(
        sales,
        lookup,
    )

    assert sale_totals == [5.5, 5.0]
    assert global_total == 10.5


def test_invalid_data_keeps_execution_and_reports_errors(capsys) -> None:
    """It skips invalid records and reports issues to console."""
    compute_sales = load_module()

    lookup = {"apple": 2.0}
    sales = [
        {"items": ["apple", {"title": "orange", "quantity": 2}]},
        {"items": [{"title": "apple", "quantity": -1}]},
        {"items": [42]},
    ]

    sale_totals, global_total = compute_sales.compute_sales_totals(
        sales,
        lookup,
    )
    captured = capsys.readouterr()

    assert sale_totals == [2.0, 0.0, 0.0]
    assert global_total == 2.0
    assert "ERROR:" in captured.out


def test_main_writes_sales_results_file(tmp_path, monkeypatch, capsys) -> None:
    """Main prints and persists a human-readable report."""
    compute_sales = load_module()

    catalogue_path = tmp_path / "priceCatalogue.json"
    sales_path = tmp_path / "salesRecord.json"

    write_json(catalogue_path, [{"title": "pen", "price": 10}])
    write_json(
        sales_path,
        [{"items": ["pen", {"title": "pen", "quantity": 2}]}],
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["computeSales.py", str(catalogue_path), str(sales_path)],
    )

    code = compute_sales.main()
    captured = capsys.readouterr()
    results_file = tmp_path / "SalesResults.txt"

    assert code == 0
    assert results_file.exists()
    assert "Grand Total: $30.00" in results_file.read_text(encoding="utf-8")
    assert "Elapsed time:" in captured.out
