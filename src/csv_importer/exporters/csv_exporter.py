import pandas as pd
from csv_importer.result import ImportResult

def export(records: list[dict], path: str) -> None:
    df = pd.DataFrame(records)
    df.to_csv(path, index=False)
