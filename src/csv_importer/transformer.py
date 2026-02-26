import pandas as pd
import re
from typing import Any
from .constants import (
    DYNAMIC_MODE_MAP,
    DYNAMIC_MODE_PIVOT,
    DYNAMIC_MODE_YEAR_MONTH_MAP,
)

# -------------------------
# Month Mapping
# -------------------------

GERMAN_MONTHS = {
    "januar": 1,
    "februar": 2,
    "märz": 3,
    "maerz": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "dezember": 12,
}


# -------------------------
# Main Spec Application
# -------------------------

def apply_spec(df: pd.DataFrame, spec: dict):
    output = pd.DataFrame()
    errors = []

    output["_original_row"] = df["_original_row"]

    # -------------------------
    # 1. Static column mapping
    # -------------------------
    for col in spec["columns"]:
        source = col["source"]
        target = col["target"]

        if source not in df.columns:
            continue

        series = df[source]
        series = apply_transforms(series, col)
        series = cast_type(series, col)

        output[target] = series

    # -------------------------
    # 2. Dynamic columns
    # -------------------------
    for dyn in spec.get("dynamic_columns", []):
        pattern = re.compile(dyn["pattern"])
        mode = dyn.get("mode", DYNAMIC_MODE_MAP)
        numeric = dyn.get("numeric_clean", False)

        matching_columns = [c for c in df.columns if pattern.match(c)]

        if mode == DYNAMIC_MODE_MAP:
            prefix = dyn.get("target_prefix", "")

            for col_name in matching_columns:
                new_name = f"{prefix}{sanitize_column(col_name)}"

                if numeric:
                    output[new_name] = df[col_name].apply(clean_numeric_value)
                else:
                    output[new_name] = df[col_name]

        elif mode == DYNAMIC_MODE_PIVOT:
            target_field = dyn["target"]

            def build_pivot(row):
                items = []
                for col_name in matching_columns:
                    value = row[col_name]
                    if pd.isna(value) or value == "":
                        continue

                    if numeric:
                        cleaned = clean_numeric_value(value)
                        items.append({
                            "column": col_name,
                            "value": cleaned
                        })
                    else:
                        items.append({
                            "column": col_name,
                            "value": value
                        })
                return items

            output[target_field] = df.apply(build_pivot, axis=1)

        elif mode == DYNAMIC_MODE_YEAR_MONTH_MAP:
            target_field = dyn["target"]

            def build_cashflow(row):
                cashflows = {}

                for col_name in matching_columns:
                    ym = parse_year_month(col_name)
                    if not ym:
                        continue

                    value = row[col_name]

                    if pd.isna(value) or value == "":
                        cashflows[ym] = None
                        continue

                    if numeric:
                        cleaned = clean_numeric_value(value)
                        cashflows[ym] = cleaned
                    else:
                        cashflows[ym] = value

                return cashflows

            output[target_field] = df.apply(build_cashflow, axis=1)

    # -------------------------
    # 3. Computed columns
    # -------------------------
    for comp in spec.get("computed_columns", []):
        target = comp["target"]
        expr = comp["expression"]
        drop_sources = comp.get("drop_sources", False)

        output[target] = output.apply(
            lambda row: safe_eval(expr, row.to_dict()),
            axis=1
        )

        if drop_sources:
            for key in extract_expression_variables(expr):
                if key in output.columns:
                    output = output.drop(columns=[key])

    # -------------------------
    # 4. Required validation
    # -------------------------
    valid_rows = []

    for _, row in output.iterrows():
        row_errors = []
        original_row = int(row["_original_row"])

        for col in spec["columns"]:
            target = col["target"]
            required = col.get("required", False)

            if required:
                value = row.get(target)
                if pd.isna(value) or value == "":
                    row_errors.append({
                        "row": original_row,
                        "column": target,
                        "error": "Missing required value"
                    })

        if row_errors:
            errors.extend(row_errors)
        else:
            valid_rows.append(row)

    clean_df = pd.DataFrame(valid_rows)

    if "_original_row" in clean_df.columns:
        clean_df = clean_df.drop(columns=["_original_row"])

    return clean_df, errors


# -------------------------
# Helpers
# -------------------------

def apply_transforms(series: pd.Series, col_spec: dict) -> pd.Series:
    series = series.astype(str).str.strip()

    # 🔥 Fix malformed 5-digit year BEFORE type casting
    def fix_year(value):
        if pd.isna(value):
            return value

        value = str(value).strip()

        parts = value.split(".")
        if len(parts) == 3:
            day, month, year = parts
            if len(year) == 5 and year.startswith("20"):
                return f"{day}.{month}.{year[:4]}"

        return value


    if col_spec.get("type") == "date":
        series = series.apply(fix_year)

    for transform in col_spec.get("transform", []):
        if transform == "lowercase":
            series = series.str.lower()
        elif transform == "uppercase":
            series = series.str.upper()
        elif transform == "titlecase":
            series = series.str.title()

    return series



def cast_type(series: pd.Series, col_spec: dict) -> pd.Series:
    t = col_spec.get("type")

    if t == "integer":
        return pd.to_numeric(series, errors="coerce")

    if t == "float":
        return pd.to_numeric(series, errors="coerce")

    if t == "date":
        formats = col_spec.get("formats")
        single_format = col_spec.get("format")

        if formats:
            def parse_multi(value):

                if pd.isna(value) or value == "":
                    return pd.NaT

                value = str(value).strip()

                for fmt in formats:
                    try:
                        return pd.to_datetime(value, format=fmt)
                    except ValueError:
                        continue

                return pd.NaT

            return series.apply(parse_multi)

        elif single_format:
            return pd.to_datetime(series, format=single_format, errors="coerce")

        else:
            return pd.to_datetime(series, errors="coerce")


    return series


def clean_numeric_value(value: Any):
    if pd.isna(value) or value == "":
        return None

    value = str(value).strip()

    try:
        cleaned = (
            value
            .replace("€", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )
        return float(cleaned)
    except ValueError:
        return value


def parse_year_month(column_name: str):
    name = column_name.strip().lower()

    match = re.match(r"([a-zäöü]+)\s*'?(\d{2})", name)
    if not match:
        return None

    month_name = match.group(1).replace("ä", "ae")
    year_short = match.group(2)

    if month_name not in GERMAN_MONTHS:
        return None

    month_number = GERMAN_MONTHS[month_name]
    year_full = 2000 + int(year_short)

    return f"{year_full}-{month_number:02d}"


def safe_eval(expression: str, context: dict):
    clean_context = {}

    for k, v in context.items():
        if pd.isna(v):
            clean_context[k] = ""
        else:
            clean_context[k] = v

    try:
        return eval(expression, {"__builtins__": {}}, clean_context)
    except Exception:
        return None


def extract_expression_variables(expression: str):
    return re.findall(r"\b[a-zA-Z_]\w*\b", expression)


def sanitize_column(name: str):
    return (
        name.lower()
        .replace(" ", "_")
        .replace("'", "")
        .replace(".", "")
    )
