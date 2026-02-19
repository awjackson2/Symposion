from __future__ import annotations
from typing import List
from ..models import Message

class DaedAgent:
    name = "DAED"

    def handle(self, msg: Message) -> List[Message]:
        plan = (
            "PLAN:\n"
            "1) Gather context (Athen)\n"
            "2) Build deliverable (Heph)\n"
            "3) Evaluate + finalize (Nem -> Clio)\n"
        )

        # Only trigger research on structured goal
        if msg.intent == "STRUCTURED_GOAL":
            return [Message(
                sender=self.name,
                recipient="ATHEN",
                task_id=msg.task_id,
                intent="RESEARCH_REQUEST",
                content=msg.content,
                goal_reference=msg.goal_reference,
                urgency=msg.urgency
            )]

        # Only trigger build after context arrives
        if msg.intent == "CONTEXT_BRIEF":
            return [Message(
                sender=self.name,
                recipient="HEPH",
                task_id=msg.task_id,
                intent="BUILD_TASK",
                content=plan + "\n" + msg.content,
                goal_reference=msg.goal_reference,
                urgency=msg.urgency,
                meta={"plan": plan}
            )]

        # Ignore everything else
        return []

