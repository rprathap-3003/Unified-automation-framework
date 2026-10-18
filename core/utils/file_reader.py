"""File reader utility for JSON, YAML, and CSV test fixtures."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List
import yaml


class FileReader:
    """Helper class to load test fixtures across formats."""

    @staticmethod
    def load_json(file_path: str | Path) -> Dict[str, Any] | List[Any]:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_yaml(file_path: str | Path) -> Dict[str, Any]:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def load_csv(file_path: str | Path) -> List[Dict[str, str]]:
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
