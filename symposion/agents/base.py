from __future__ import annotations

from dataclasses import asdict
from typing import List
from ..models import Message

class BaseAgent:
    name: str = "BASE"

    def handle(self, msg: Message) -> List[Message]:
        self._validate(msg)
        self.on_message(msg)
        out = self.process(msg)
        for m in out:
            self._validate(m)
        return out

    def process(self, msg: Message) -> List[Message]:
        raise NotImplementedError

    def on_message(self, msg: Message) -> None:
        # Override for custom logging/metrics if desired.
        pass

    def _validate(self, msg: Message) -> None:
        # Minimal v0 validation; schema validation can be added later.
        required = ["sender","recipient","task_id","intent","content","goal_reference","urgency", "timestamp"]
        for k in required:
            if getattr(msg, k, None) in (None, ""):
                raise ValueError(f"{self.name}: missing field {k}")
