from __future__ import annotations

from uuid import uuid4

from .registry import AgentRegistry
from .result_handler import AgentResult


class Executor:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def run(self, agent_name: str, action: str, **kwargs) -> AgentResult:
        task_id = uuid4().hex
        spec = self.registry.get(agent_name)
        try:
            value = spec.handler(action=action, **kwargs)
            if isinstance(value, AgentResult):
                # The Executor owns workflow identity, so every specialist
                # result gets the same task ID even when the specialist did
                # not create one itself.
                if not value.task_id:
                    value.task_id = task_id
                if not value.agent:
                    value.agent = agent_name
                return value
            return AgentResult(
                agent=agent_name,
                task_id=task_id,
                status="success",
                summary=f"{agent_name} completed {action}.",
                outputs=[value] if value is not None else [],
            )
        except Exception as exc:
            return AgentResult(
                agent=agent_name,
                task_id=task_id,
                status="failed",
                summary=f"{agent_name} failed during {action}.",
                errors=[str(exc)],
            )
