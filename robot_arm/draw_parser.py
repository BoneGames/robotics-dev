"""Parser for selecting the round/draw action for the robot arm."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


DRAW_CSV_PATH = Path(__file__).resolve().parents[1] / "draw.csv"


def _parse_round_datetime(raw_value: str) -> datetime:
    raw_value = raw_value.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw_value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {raw_value}")


def get_round() -> int | None:
    """Return the 1-based row number for the next upcoming game round.

    Column 3 in draw.csv must contain the game date in one of these formats:
    YYYY-MM-DD or YYYY-MM-DD HH:MM.
    """

    now = datetime.now()
    next_row_number: int | None = None
    next_round_time: datetime | None = None

    with DRAW_CSV_PATH.open("r", newline="", encoding="utf-8") as draw_file:
        reader = csv.reader(draw_file)
        for row_number, row in enumerate(reader, start=1):
            if len(row) < 3 or not row[2].strip():
                continue

            round_time = _parse_round_datetime(row[2])
            if round_time < now:
                continue

            if next_round_time is None or round_time < next_round_time:
                next_round_time = round_time
                next_row_number = row_number
                
    print(f"next round row: {next_row_number}")
    return next_row_number
