from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    handler: Callable[..., Any]


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, AgentSpec] = {}

    def register(self, name: str, description: str, handler: Callable[..., Any]) -> None:
        if name in self._agents:
            raise ValueError(f"Agent already registered: {name}")
        self._agents[name] = AgentSpec(name, description, handler)

    def get(self, name: str) -> AgentSpec:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {name}") from exc

    def names(self) -> list[str]:
        return sorted(self._agents)

    def describe(self) -> dict[str, str]:
        return {name: spec.description for name, spec in self._agents.items()}
