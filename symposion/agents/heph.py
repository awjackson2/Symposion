from __future__ import annotations
from typing import List
from ..models import Message
from ..protocol.intent import Intent

class HephAgent:
    """Heph builds artifacts. In v0 it creates a draft, then a revised artifact when requested."""
    name = "HEPH"

    def handle(self, msg: Message) -> List[Message]:
        if msg.intent == Intent.REVISION_REQUEST.value:
            artifact = (
                "ARTIFACT (REVISED):\n"
                "Roadmap (Short + Structured)\n"
                "- Alpha: single-machine prototype with message logging and Nem review gate.\n"
                "- Beta: agents as services + async messaging + persistent storage.\n"
                "- Meson: scaling + memory + negotiation loops + observability.\n"
                "- Telos: standardization + SDK + plugins + production readiness.\n\n"
                "How Nem enforces quality:\n"
                "- Nem evaluates Heph outputs against the original objective.\n"
                "- If misaligned/incomplete: returns REVISION_REQUEST with required changes.\n"
                "- Heph revises and resubmits until APPROVED or escalation.\n\n"
                "Requested Changes Addressed:\n"
                "- Provided concrete deliverable aligned to OBJECTIVE.\n"
                "- Included step-by-step structure.\n"
            )
            return [Message(
                sender=self.name,
                recipient="NEM",
                task_id=msg.task_id,
                intent=Intent.ARTIFACT_BUILT.value,
                content=artifact,
                goal_reference=msg.goal_reference,
                urgency=msg.urgency,
                meta={"revised": True}
            )]

        # Default: BUILD_TASK and anything else treated as initial build
        artifact = (
            "ARTIFACT (DRAFT):\n"
            "This is a placeholder deliverable produced by Heph in v0.\n\n"
            "INPUT:\n"
            f"{msg.content}\n"
        )
        return [Message(
            sender=self.name,
            recipient="NEM",
            task_id=msg.task_id,
            intent=Intent.ARTIFACT_BUILT.value,
            content=artifact,
            goal_reference=msg.goal_reference,
            urgency=msg.urgency,
            meta={"revised": False}
        )]
