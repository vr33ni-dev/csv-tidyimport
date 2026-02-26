import math
import pandas as pd
from typing import Any


def normalize_value(value: Any) -> Any:
    if isinstance(value, float) and math.isnan(value):
        return None

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value


def normalize_record(record: dict) -> dict:
    return {k: normalize_value(v) for k, v in record.items()}


def normalize_records(records: list[dict]) -> list[dict]:
    normalized = []
    former_mode = False

    for raw_record in records:
        # 🔥 first normalize pandas values
        record = normalize_record(raw_record)

        name = (record.get("name") or "").strip()

        # Detect marker row
        if name.lower() == "ehemalige":
            former_mode = True
            continue

        # Skip empty rows
        if not name:
            continue

        # Add flag
        record["is_former"] = former_mode

        normalized.append(record)

    return normalized
