from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List
from ..models import Message
from .registry import AgentRegistry
from .messaging import MessageBus
from ..utils.logging import JsonlLogger

class Orchestrator:
    """Routes messages to agents and enforces the Nemesis gate."""

    def __init__(self, registry: AgentRegistry, bus: MessageBus, logger: JsonlLogger):
        self.registry = registry
        self.bus = bus
        self.logger = logger
        self.task_state: Dict[str, Dict] = {}  # keyed by task_id
        self.completed_tasks: set[str] = set()

    def bootstrap(self, first: Message) -> None:
        self.bus.send(first)

    def run(self, max_steps: int = 200) -> None:
        def is_final_report(m: Message) -> bool:
            return m.sender == "CLIO" and m.recipient == "HUMAN" and m.intent == "FINAL_REPORT"

        steps = 0
        while steps < max_steps:
            steps += 1
            batch = self.bus.drain()
            if not batch:
                break

            for msg in batch:
                # Drop messages for tasks already completed, BUT never drop the final report delivery itself.
                if msg.task_id in self.completed_tasks and not is_final_report(msg):
                    self.logger.log({
                        "type": "message_dropped_task_completed",
                        "message": asdict(msg),
                        "reason": "task_already_completed"
                    })
                    continue

                self.logger.log({"type": "message_routed", "message": asdict(msg)})

                # Deliver message to its recipient
                agent = self.registry.get(msg.recipient)
                out = agent.handle(msg)

                # IMPORTANT: Mark completion only after the FINAL_REPORT has been routed/delivered to HUMAN.
                if is_final_report(msg):
                    self.completed_tasks.add(msg.task_id)
                    self.logger.log({
                        "type": "task_completed",
                        "task_id": msg.task_id,
                        "goal_reference": msg.goal_reference
                    })
                    # After final delivery, we can safely ignore any outputs produced by HUMAN (usually none).
                    continue

                for out_msg in out:
                    # Nemesis gate rule (hard-coded v0):
                    # Any artifact produced by HEPH must be evaluated by NEM before reaching CLIO.
                    if out_msg.sender == "HEPH" and out_msg.intent in ("ARTIFACT_BUILT", "ARTIFACT"):
                        if out_msg.recipient != "NEM":
                            out_msg = Message(
                                sender=out_msg.sender,
                                recipient="NEM",
                                task_id=out_msg.task_id,
                                intent=out_msg.intent,
                                content=out_msg.content,
                                goal_reference=out_msg.goal_reference,
                                urgency=out_msg.urgency,
                                timestamp=out_msg.timestamp,
                                meta=dict(out_msg.meta),
                            )

                    # Drop outgoing messages for tasks already completed (no need to allow FINAL_REPORT here,
                    # because completion is only set when FINAL_REPORT is routed, not when it's emitted).
                    if out_msg.task_id in self.completed_tasks:
                        self.logger.log({
                            "type": "message_dropped_task_completed",
                            "message": asdict(out_msg),
                            "reason": "task_already_completed"
                        })
                        continue

                    self.bus.send(out_msg)

        self.logger.log({"type": "orchestrator_stopped", "steps": steps})

