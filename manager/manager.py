from __future__ import annotations

from pathlib import Path
from typing import Any

from .executor import Executor
from .planner import Planner
from .registry import AgentRegistry
from .result_handler import AgentResult


class Manager:
    """Jarvis orchestration core. Specialist work remains inside specialist agents."""

    def __init__(self) -> None:
        self.registry = AgentRegistry()
        self.planner = Planner()
        self.executor = Executor(self.registry)

    def register_agent(self, name: str, description: str, handler) -> None:
        self.registry.register(name, description, handler)

    def handle(self, request: str, **context: Any) -> list[AgentResult]:
        plan = self.planner.plan(request)
        if not plan:
            return [AgentResult(
                agent="manager",
                task_id="",
                status="needs_input",
                summary="I could not map the request to a registered workflow yet.",
                errors=["No execution plan was produced."],
            )]

        results: list[AgentResult] = []
        for step in plan:
            results.append(self.executor.run(step.agent, step.action, **context))
            if not results[-1].success:
                break
        return results


def create_default_manager() -> Manager:
    """Create a Manager with the current V1 Product Agent registered."""
    from agents.product_agent.agent import handle_product_task

    manager = Manager()
    manager.register_agent(
        "product_agent",
        "Product images and product-data preparation, including the V1 image optimizer.",
        handle_product_task,
    )
    return manager
