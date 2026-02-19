from __future__ import annotations
from dataclasses import asdict
from typing import List
from ..models import Message
from ..utils.logging import JsonlLogger

class MessageBus:
    """In-memory message bus with JSONL logging (v0)."""
    def __init__(self, logger: JsonlLogger):
        self.logger = logger
        self.queue: List[Message] = []

    def send(self, msg: Message) -> None:
        self.queue.append(msg)
        self.logger.log({"type": "message_enqueued", "message": asdict(msg)})

    def drain(self) -> List[Message]:
        batch = self.queue
        self.queue = []
        return batch
