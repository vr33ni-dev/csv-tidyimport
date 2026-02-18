import pandas as pd


def load_file(filepath: str) -> pd.DataFrame:
    if filepath.endswith(".xlsx"):
        return pd.read_excel(filepath)
    return pd.read_csv(filepath)
