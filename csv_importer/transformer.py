import pandas as pd


def apply_spec(df: pd.DataFrame, spec: dict) -> pd.DataFrame:
    output = pd.DataFrame()

    for col in spec["columns"]:
        source = col["source"]
        target = col["target"]

        series = df[source]

        series = apply_transforms(series, col)
        series = cast_type(series, col)

        output[target] = series

    return output


def apply_transforms(series: pd.Series, col_spec: dict) -> pd.Series:
    for transform in col_spec.get("transform", []):
        if transform == "trim":
            series = series.astype(str).str.strip()

        if transform == "lowercase":
            series = series.str.lower()

    return series


def cast_type(series: pd.Series, col_spec: dict) -> pd.Series:
    t = col_spec.get("type")

    if t == "integer":
        return pd.to_numeric(series, errors="coerce")

    if t == "date":
        fmt = col_spec.get("format")
        return pd.to_datetime(series, format=fmt, errors="coerce")

    return series
