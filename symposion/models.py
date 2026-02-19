from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Dict, Any
import time
import uuid

Urgency = Literal["LOW", "NORMAL", "HIGH", "CRITICAL"]

def new_task_id(prefix: str = "TASK") -> str:
    return f"{prefix}-{uuid.uuid4()}"

def now_ts() -> float:
    return time.time()

@dataclass(frozen=True)
class Message:
    sender: str
    recipient: str
    task_id: str
    intent: str
    content: str
    goal_reference: str
    urgency: Urgency = "NORMAL"
    timestamp: float = field(default_factory=now_ts)
    meta: Dict[str, Any] = field(default_factory=dict)
