from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentRequest:
    message: str
    user_id: str = "demo-user"
    session_id: str = "demo-session"


@dataclass
class TraceStep:
    name: str
    input: str
    output: str


@dataclass
class AgentResponse:
    answer: str
    intent: str
    used_tools: list[str] = field(default_factory=list)
    citations: list[dict[str, Any]] = field(default_factory=list)
    trace: list[TraceStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "intent": self.intent,
            "used_tools": self.used_tools,
            "citations": self.citations,
            "trace": [step.__dict__ for step in self.trace],
        }

