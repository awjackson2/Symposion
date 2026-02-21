from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet

from .intent import Intent


@dataclass(frozen=True)
class IntentRule:
    intent: Intent
    allowed_senders: FrozenSet[str]
    allowed_recipients: FrozenSet[str]
    required_meta_keys: FrozenSet[str] = frozenset()


INTENT_RULES: Dict[Intent, IntentRule] = {
    Intent.NEW_GOAL: IntentRule(
        intent=Intent.NEW_GOAL,
        allowed_senders=frozenset({"HUMAN"}),
        allowed_recipients=frozenset({"HERM"}),
    ),
    Intent.STRUCTURED_GOAL: IntentRule(
        intent=Intent.STRUCTURED_GOAL,
        allowed_senders=frozenset({"HERM"}),
        allowed_recipients=frozenset({"DAED"}),
        required_meta_keys=frozenset({"source_intent"}),
    ),
    Intent.RESEARCH_REQUEST: IntentRule(
        intent=Intent.RESEARCH_REQUEST,
        allowed_senders=frozenset({"DAED"}),
        allowed_recipients=frozenset({"ATHEN"}),
    ),
    Intent.CONTEXT_BRIEF: IntentRule(
        intent=Intent.CONTEXT_BRIEF,
        allowed_senders=frozenset({"ATHEN"}),
        allowed_recipients=frozenset({"DAED"}),
    ),
    Intent.BUILD_TASK: IntentRule(
        intent=Intent.BUILD_TASK,
        allowed_senders=frozenset({"DAED"}),
        allowed_recipients=frozenset({"HEPH"}),
    ),
    Intent.ARTIFACT_BUILT: IntentRule(
        intent=Intent.ARTIFACT_BUILT,
        allowed_senders=frozenset({"HEPH"}),
        allowed_recipients=frozenset({"NEM"}),
        required_meta_keys=frozenset({"revised"}),
    ),
    Intent.REVISION_REQUEST: IntentRule(
        intent=Intent.REVISION_REQUEST,
        allowed_senders=frozenset({"NEM"}),
        allowed_recipients=frozenset({"HEPH"}),
    ),
    Intent.APPROVED_OUTPUT: IntentRule(
        intent=Intent.APPROVED_OUTPUT,
        allowed_senders=frozenset({"NEM"}),
        allowed_recipients=frozenset({"CLIO"}),
    ),
    Intent.FINAL_REPORT: IntentRule(
        intent=Intent.FINAL_REPORT,
        allowed_senders=frozenset({"CLIO"}),
        allowed_recipients=frozenset({"HUMAN"}),
    ),
}
