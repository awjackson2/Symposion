from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from symposion.core.messaging import MessageBus
from symposion.core.orchestrator import Orchestrator
from symposion.core.registry import AgentRegistry
from symposion.models import Message
from symposion.protocol.intent import Intent
from symposion.protocol.validate import ProtocolViolation, validate_intent
from symposion.utils.logging import JsonlLogger


class _EchoAgent:
    def __init__(self, name: str):
        self.name = name
        self.received: list[Message] = []

    def handle(self, msg: Message):
        self.received.append(msg)
        return []


def _message(**overrides) -> Message:
    base = Message(
        sender="HUMAN",
        recipient="HERM",
        task_id="TASK-1",
        intent=Intent.NEW_GOAL.value,
        content="goal",
        goal_reference="GOAL-1",
        urgency="NORMAL",
        meta={},
    )
    return replace(base, **overrides)


def test_validate_rejects_invalid_sender_recipient_pair():
    msg = _message(sender="DAED")

    with pytest.raises(ProtocolViolation, match="Sender 'DAED' is not allowed"):
        validate_intent(msg)


def test_validate_rejects_missing_required_meta_keys():
    structured = _message(
        sender="HERM",
        recipient="DAED",
        intent=Intent.STRUCTURED_GOAL.value,
        meta={},
    )
    artifact = _message(
        sender="HEPH",
        recipient="NEM",
        intent=Intent.ARTIFACT_BUILT.value,
        meta={},
    )

    with pytest.raises(ProtocolViolation, match="source_intent"):
        validate_intent(structured)
    with pytest.raises(ProtocolViolation, match="revised"):
        validate_intent(artifact)


def test_validate_accepts_valid_messages():
    validate_intent(_message())
    validate_intent(
        _message(
            sender="HERM",
            recipient="DAED",
            intent=Intent.STRUCTURED_GOAL.value,
            meta={"source_intent": Intent.NEW_GOAL.value},
        )
    )


def test_orchestrator_drops_unknown_intent_by_default(tmp_path: Path):
    human = _EchoAgent("HUMAN")
    logger = JsonlLogger(tmp_path / "events.jsonl")
    orch = Orchestrator(
        registry=AgentRegistry(agents={"HUMAN": human}),
        bus=MessageBus(logger),
        logger=logger,
    )
    bad = _message(sender="CLIO", recipient="HUMAN", intent="UNKNOWN_INTENT")

    orch.bootstrap(bad)
    orch.run(max_steps=1)

    assert human.received == []
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text().splitlines()]
    violations = [e for e in events if e.get("type") == "protocol_violation"]
    assert len(violations) == 1
    assert "Unknown intent" in violations[0]["error"]


def test_orchestrator_raises_on_unknown_intent_in_strict_mode(tmp_path: Path):
    logger = JsonlLogger(tmp_path / "events.jsonl")
    orch = Orchestrator(
        registry=AgentRegistry(agents={"HUMAN": _EchoAgent("HUMAN")}),
        bus=MessageBus(logger),
        logger=logger,
        strict_protocol=True,
    )

    orch.bootstrap(_message(sender="CLIO", recipient="HUMAN", intent="UNKNOWN_INTENT"))

    with pytest.raises(ProtocolViolation, match="Unknown intent"):
        orch.run(max_steps=1)
