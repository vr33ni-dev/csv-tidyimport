import json
from csv_importer.result import ImportResult


def export(records: list[dict], path: str) -> None:
    with open(path, "w") as f:
        json.dump(records, f, indent=2)
