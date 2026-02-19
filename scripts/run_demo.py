from __future__ import annotations

from pathlib import Path
from symposion.models import Message, new_task_id
from symposion.utils.ids import new_goal_reference
from symposion.utils.logging import JsonlLogger
from symposion.core.registry import AgentRegistry
from symposion.core.messaging import MessageBus
from symposion.core.orchestrator import Orchestrator

from symposion.agents import HermAgent, DaedAgent, AthenAgent, MetAgent, HephAgent, NemAgent, ClioAgent

def main() -> None:
    out_dir = Path("examples/out")
    out_dir.mkdir(parents=True, exist_ok=True)

    logger = JsonlLogger(
        out_dir / f"demo_log.{new_task_id('LOG')}.jsonl"
    )

    bus = MessageBus(logger)

    registry = AgentRegistry(agents={
        "HERM": HermAgent(),
        "DAED": DaedAgent(),
        "ATHEN": AthenAgent(),
        "MET": MetAgent(),
        "HEPH": HephAgent(),
        "NEM": NemAgent(),
        "CLIO": ClioAgent(),
        # Human is not an agent in v0; the orchestrator will just print messages to HUMAN.
        "HUMAN": _HumanSink(),
    })

    orch = Orchestrator(registry=registry, bus=bus, logger=logger)

    goal_ref = new_goal_reference()
    task_id = new_task_id("TASK")

    first = Message(
        sender="HUMAN",
        recipient="HERM",
        task_id=task_id,
        intent="NEW_GOAL",
        content="Create a short, structured roadmap for Symposion and explain how Nem enforces quality.",
        goal_reference=goal_ref,
        urgency="NORMAL",
    )

    orch.bootstrap(first)
    orch.run(max_steps=10)

class _HumanSink:
    name = "HUMAN"
    def handle(self, msg: Message):
        print("\n=== MESSAGE TO HUMAN ===")
        print(msg.content)
        return []

if __name__ == "__main__":
    main()
