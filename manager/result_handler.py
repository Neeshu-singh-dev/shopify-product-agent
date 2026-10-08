from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResult:
    agent: str
    task_id: str
    status: str
    summary: str = ""
    outputs: list[Any] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.status == "success"

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "task_id": self.task_id,
            "status": self.status,
            "summary": self.summary,
            "outputs": self.outputs,
            "statistics": self.statistics,
            "errors": self.errors,
        }
