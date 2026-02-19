from __future__ import annotations
from typing import List
from ..models import Message

class AthenAgent:
    name = "ATHEN"

    def handle(self, msg: Message) -> List[Message]:
        brief = (
            "CONTEXT_BRIEF:\n"
            "- This is a starter prototype; replace Athen with real research later.\n"
            "- Provide definitions, constraints, and references as needed.\n"
        )

        return [Message(
            sender=self.name,
            recipient=msg.sender,  # reply to whoever asked
            task_id=msg.task_id,
            intent="CONTEXT_BRIEF",
            content=brief,
            goal_reference=msg.goal_reference,
            urgency=msg.urgency
        )]
