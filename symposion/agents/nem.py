from __future__ import annotations
from typing import List
from ..models import Message

class NemAgent:
    """Nem judges Heph outputs for quality + goal alignment."""
    name = "NEM"

    def handle(self, msg: Message) -> List[Message]:
        # v0: simplistic heuristic—always request one revision unless meta says 'revised'.
        revised = bool(msg.meta.get("revised", False))

        if not revised:
            feedback = (
                "VERDICT: REVISION_REQUIRED\n"
                "REASONS:\n"
                "- Deliverable is a placeholder draft; add concrete content.\n"
                "REQUIRED_CHANGES:\n"
                "1) Provide a clear, usable output aligned to OBJECTIVE.\n"
                "2) Add step-by-step guidance or structure.\n"
            )
            # send revision request back to Heph
            return [Message(
                sender=self.name,
                recipient="HEPH",
                task_id=msg.task_id,
                intent="REVISION_REQUEST",
                content=feedback,
                goal_reference=msg.goal_reference,
                urgency=msg.urgency,
                meta={"revised": True}  # next pass will approve
            )]

        verdict = (
            "VERDICT: APPROVED\n"
            "NOTES:\n"
            "- Output meets minimum criteria for v0 demo.\n"
        )
        return [Message(
            sender=self.name,
            recipient="CLIO",
            task_id=msg.task_id,
            intent="APPROVED_OUTPUT",
            content=verdict + "\n" + msg.content,
            goal_reference=msg.goal_reference,
            urgency=msg.urgency
        )]
