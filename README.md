# csv-tidyimport

YAML-driven CSV/Excel clean-and-transform library

## Idea

messy.csv / messy.xlsx
        ↓
rules.yaml
        ↓
normalized structured records
        ↓
clean.json / clean.csv / DB insert (handled by application or CLI)

## Architecture

```mermaid
flowchart TD

    A["CLI or Application"] --> B["Load Spec (rules.yaml)"]
    B --> C["ImportEngine"]

    C --> D["load_file (CSV/XLSX)"]
    D --> E["apply_spec"]
    E --> F["Column Transforms"]
    F --> G["Type Casting"]
    G --> H["ImportResult (records + errors)"]

    H --> I{"Output Layer"}
    I --> J["CSV Exporter"]
    I --> K["JSON Exporter"]
    I --> L["Application DB Insert"]

```
