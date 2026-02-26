from csv_importer.result import ImportResult
from .loader import load_file
from .transformer import apply_spec
from .spec_validator import validate_spec
from .utils import normalize_records   # 👈 new import


class ImportEngine:

    def __init__(self, spec: dict):
        validate_spec(spec)
        self.spec = spec

    def run(self, filepath: str) -> ImportResult:
        df = load_file(filepath, self.spec)

        clean_df, errors = apply_spec(df, self.spec)

        raw_records = clean_df.to_dict(orient="records")

        # 🔥 normalize pandas types here
        records = normalize_records(raw_records)

        return ImportResult(
            records=records,
            errors=errors
        )
