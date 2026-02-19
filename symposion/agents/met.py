from __future__ import annotations
from typing import List
from ..models import Message

class MetAgent:
    """Met mediates conflicts. In v0 it simply forwards the preferred option."""
    name = "MET"

    def handle(self, msg: Message) -> List[Message]:
        decision = (
            "DECISION:\n"
            "- No conflict resolution implemented in v0.\n"
            "- Treat this message as an alignment checkpoint.\n"
        )
        return [Message(
            sender=self.name,
            recipient="DAED",
            task_id=msg.task_id,
            intent="CONSENSUS_DECISION",
            content=decision,
            goal_reference=msg.goal_reference,
            urgency=msg.urgency
        )]
