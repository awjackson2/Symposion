from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Protocol, List
from ..models import Message

class Agent(Protocol):
    name: str
    def handle(self, msg: Message) -> List[Message]: ...

@dataclass
class AgentRegistry:
    agents: Dict[str, Agent]

    def get(self, name: str) -> Agent:
        if name not in self.agents:
            raise KeyError(f"Unknown agent: {name}")
        return self.agents[name]
