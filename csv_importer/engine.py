from csv_importer.result import ImportResult
from .loader import load_file
from .transformer import apply_spec


class ImportEngine:

    def __init__(self, spec: dict):
        self.spec = spec

    def run(self, filepath: str) -> ImportResult:
        df = load_file(filepath)
        clean_df = apply_spec(df, self.spec)

        # Convert this table into a list of row dictionaries. (opposed to orient=dict or list)
        records = clean_df.to_dict(orient="records")

        return ImportResult(
            records=records,
            errors=[]
        )
