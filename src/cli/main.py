# cli/main.py

import argparse
import sys

from csv_importer.engine import ImportEngine
from csv_importer.spec import load_spec
from csv_importer.exporters import csv_exporter, json_exporter

from .db_handler import insert_records


def parse_args():
    parser = argparse.ArgumentParser(description="Tidy Import CLI")

    parser.add_argument("input", nargs="?", help="Input CSV or Excel file")
    parser.add_argument("--spec", help="Path to rules.yaml")
    parser.add_argument("--format", choices=["csv", "json", "db"])
    parser.add_argument("--output", help="Output file path (for csv/json)")

    args = parser.parse_args()

    if not args.input:
        args.input = input("Enter input file path: ")

    if not args.spec:
        args.spec = input("Enter spec file path: ")

    if not args.format:
        args.format = input("Enter output format (csv/json/db): ").strip()

    if args.format in ["csv", "json"] and not args.output:
        args.output = input("Enter output file path: ")

    return args


def main():
    args = parse_args()

    try:
        spec = load_spec(args.spec)
        engine = ImportEngine(spec)

        result = engine.run(args.input) 

        if result.errors:
            print(f"Import completed with {len(result.errors)} validation errors.")
            for err in result.errors:
                print(f"Row {err['row']} - {err['column']}: {err['error']}")

            print("Valid rows exported successfully.")
        else:
            print("Import completed successfully.")

        if args.format == "csv":
            csv_exporter.export(result.records, args.output)

        elif args.format == "json":
            json_exporter.export(result.records, args.output)

        elif args.format == "db":
            insert_records(result.records)


        print("Import completed successfully.")

    except Exception as e:
        print(f"Import failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
