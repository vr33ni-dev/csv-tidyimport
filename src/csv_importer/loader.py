import pandas as pd


def load_file(filepath: str, spec: dict) -> pd.DataFrame:
    input_spec = spec.get("input", {})

    skip_rows = input_spec.get("skip_rows", 0)
    header_row = input_spec.get("header_row", 1)
    delimiter = input_spec.get("delimiter", ",")

    df = pd.read_csv(
        filepath,
        skiprows=skip_rows,
        header=header_row - 1,
        sep=delimiter
    )

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Compute original file line numbers
    base_offset = skip_rows + header_row
    df["_original_row"] = df.index + base_offset + 1

    return df
