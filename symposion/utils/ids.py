from __future__ import annotations
import uuid

def new_goal_reference(prefix: str = "GOAL") -> str:
    return f"{prefix}-{uuid.uuid4()}"
