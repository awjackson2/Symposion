from __future__ import annotations
from typing import List
from ..models import Message
from ..protocol.intent import Intent

class HermAgent:
    """Herm interprets human goals and produces a structured goal."""
    name = "HERM"

    def handle(self, msg: Message) -> List[Message]:
        # v0: no deep parsing; just wrap in a structured template.
        structured = (
            f"OBJECTIVE: {msg.content}\n"
            f"SCOPE: (define)\n"
            f"CONSTRAINTS: (define)\n"
            f"SUCCESS_CRITERIA: (define)\n"
            f"ASSUMPTIONS: (define)\n"
        )

        return [Message(
            sender=self.name,
            recipient="DAED",
            task_id=msg.task_id,
            intent=Intent.STRUCTURED_GOAL.value,
            content=structured,
            goal_reference=msg.goal_reference,
            urgency=msg.urgency,
            meta={"source_intent": msg.intent},
        )]
