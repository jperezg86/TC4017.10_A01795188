"""Utilidades de persistencia basadas en archivos JSONL."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jsonl(file_path: Path, entity_name: str) -> list[dict[str, Any]]:
    """Carga registros JSONL y omite líneas inválidas sin detener ejecución."""
    if not file_path.exists():
        return []

    records: list[dict[str, Any]] = []
    with file_path.open("r", encoding="utf-8") as file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    "ERROR: línea inválida en "
                    f"{entity_name} ({file_path}, línea {line_number}): {exc}"
                )
                continue

            if not isinstance(payload, dict):
                print(
                    "ERROR: formato inválido en "
                    f"{entity_name} ({file_path}, línea {line_number})"
                )
                continue

            records.append(payload)

    return records


def save_jsonl(
    file_path: Path,
    records: list[dict[str, Any]],
) -> None:
    """Guarda una lista de registros como JSONL."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=True) + "\n")
