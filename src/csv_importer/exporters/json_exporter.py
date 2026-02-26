import json
from csv_importer.result import ImportResult


def export(records: list[dict], path: str) -> None:
    # Use a permissive default serializer so objects like pandas.Timestamp
    # are converted to strings (ISO format) instead of raising an error.
    with open(path, "w") as f:
        json.dump(records, f, indent=2, default=str)
