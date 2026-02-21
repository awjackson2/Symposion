from __future__ import annotations

from typing import Iterable

from ..models import Message
from .intent import Intent
from .taxonomy import INTENT_RULES


class ProtocolViolation(Exception):
    pass


def _format_allowed(values: Iterable[str]) -> str:
    return ", ".join(sorted(values))


def validate_intent(msg: Message) -> Intent:
    try:
        intent = msg.intent if isinstance(msg.intent, Intent) else Intent(msg.intent)
    except ValueError as exc:
        raise ProtocolViolation(
            f"Unknown intent '{msg.intent}' for sender='{msg.sender}' recipient='{msg.recipient}'."
        ) from exc

    rule = INTENT_RULES[intent]

    if msg.sender not in rule.allowed_senders:
        raise ProtocolViolation(
            f"Sender '{msg.sender}' is not allowed for intent '{intent.value}'. "
            f"Allowed senders: [{_format_allowed(rule.allowed_senders)}]. "
            f"recipient='{msg.recipient}'."
        )

    if msg.recipient not in rule.allowed_recipients:
        raise ProtocolViolation(
            f"Recipient '{msg.recipient}' is not allowed for intent '{intent.value}'. "
            f"Allowed recipients: [{_format_allowed(rule.allowed_recipients)}]. "
            f"sender='{msg.sender}'."
        )

    missing_keys = sorted(k for k in rule.required_meta_keys if k not in msg.meta)
    if missing_keys:
        raise ProtocolViolation(
            f"Missing required meta keys for intent '{intent.value}': {missing_keys}. "
            f"sender='{msg.sender}' recipient='{msg.recipient}'."
        )

    return intent
