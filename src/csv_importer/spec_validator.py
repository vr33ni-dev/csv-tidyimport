from .constants import DYNAMIC_COLUMN_MODES

class SpecValidationError(Exception):
    pass


def validate_spec(spec: dict):
    if not isinstance(spec, dict):
        raise SpecValidationError("Spec must be a dictionary")

    # -------------------------
    # Required: columns
    # -------------------------
    if "columns" not in spec:
        raise SpecValidationError("Spec must contain 'columns' section")

    if not isinstance(spec["columns"], list):
        raise SpecValidationError("'columns' must be a list")

    for col in spec["columns"]:
        if not isinstance(col, dict):
            raise SpecValidationError("Each column definition must be a dictionary")

        if "source" not in col:
            raise SpecValidationError("Each column must define 'source'")

        if "target" not in col:
            raise SpecValidationError("Each column must define 'target'")

    # -------------------------
    # Optional: computed_columns
    # -------------------------
    if "computed_columns" in spec:
        if not isinstance(spec["computed_columns"], list):
            raise SpecValidationError("'computed_columns' must be a list")

        for comp in spec["computed_columns"]:
            if not isinstance(comp, dict):
                raise SpecValidationError("Each computed column must be a dictionary")

            if "target" not in comp:
                raise SpecValidationError("Computed column must define 'target'")

            if "expression" not in comp:
                raise SpecValidationError("Computed column must define 'expression'")

            if not isinstance(comp["expression"], str):
                raise SpecValidationError("'expression' must be a string")

    # -------------------------
    # Optional: dynamic_columns
    # -------------------------
    if "dynamic_columns" in spec:
        if not isinstance(spec["dynamic_columns"], list):
            raise SpecValidationError("'dynamic_columns' must be a list")

        for dyn in spec["dynamic_columns"]:
            if not isinstance(dyn, dict):
                raise SpecValidationError("Each dynamic column rule must be a dictionary")

            if "pattern" not in dyn:
                raise SpecValidationError("Dynamic column must define 'pattern'")

            if not isinstance(dyn["pattern"], str):
                raise SpecValidationError("'pattern' must be a string")

            if "target" not in dyn and "target_prefix" not in dyn:
                raise SpecValidationError(
                    "Dynamic column must define either 'target' or 'target_prefix'"
                )

            if "mode" in dyn and dyn["mode"] not in DYNAMIC_COLUMN_MODES:
                raise SpecValidationError(
                    f"Dynamic column 'mode' must be one of {sorted(DYNAMIC_COLUMN_MODES)}"
                )

