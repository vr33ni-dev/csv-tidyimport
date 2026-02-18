from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ImportResult:
    records: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
