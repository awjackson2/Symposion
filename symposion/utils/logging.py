from __future__ import annotations
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Optional

class JsonlLogger:
    """Very simple JSONL logger for message trails."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: dict) -> None:
        event = dict(event)
        event.setdefault("ts", time.time())
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
