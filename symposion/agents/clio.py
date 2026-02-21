from __future__ import annotations
from typing import List
from ..models import Message
from ..protocol.intent import Intent

class ClioAgent:
    """Clio narrates final results for humans."""
    name = "CLIO"

    def handle(self, msg: Message) -> List[Message]:
        report = (
            "SYMPOSION FINAL REPORT\n"
            "----------------------\n"
            f"Goal Reference: {msg.goal_reference}\n"
            f"Task ID: {msg.task_id}\n"
            f"Urgency: {msg.urgency}\n\n"
            "Summary:\n"
            "- Goal interpreted, plan created, artifact built, judged, and approved.\n\n"
            "Approved Output:\n"
            f"{msg.content}\n"
        )
        # In a real system, recipient might be a HUMAN channel; for demo we send to ORCHESTRATOR/HUMAN.
        return [Message(
            sender=self.name,
            recipient="HUMAN",
            task_id=msg.task_id,
            intent=Intent.FINAL_REPORT.value,
            content=report,
            goal_reference=msg.goal_reference,
            urgency=msg.urgency
        )]
