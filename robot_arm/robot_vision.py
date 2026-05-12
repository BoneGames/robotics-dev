"""Round-to-position lookup from draw.csv."""

from __future__ import annotations

import csv
from pathlib import Path

DRAW_CSV_PATH = Path(__file__).resolve().parents[1] / "draw.csv"
FALLBACK_POSITIONS = [2047, 856, 3069, 1212, 2045]


def get_base_positions() -> list[int]:
    """Return the default base pose for startup positioning."""

    return FALLBACK_POSITIONS.copy()


def _parse_positions(raw_value: str) -> list[int]:
    values = [item.strip() for item in raw_value.split(",") if item.strip()]
    return [int(value) for value in values]


def get_positions(round_row: int | None) -> list[int]:
    """Return target positions from column 4 for a given 1-based CSV row."""

    if round_row is None or round_row < 1:
        return FALLBACK_POSITIONS.copy()

    with DRAW_CSV_PATH.open("r", newline="", encoding="utf-8") as draw_file:
        reader = csv.reader(draw_file)
        for row_number, row in enumerate(reader, start=1):
            if row_number != round_row:
                continue

            if len(row) < 4 or not row[3].strip():
                return FALLBACK_POSITIONS.copy()

            try:
                parsed = _parse_positions(row[3])
            except ValueError:
                return FALLBACK_POSITIONS.copy()

            return parsed if parsed else FALLBACK_POSITIONS.copy()

    return FALLBACK_POSITIONS.copy()
