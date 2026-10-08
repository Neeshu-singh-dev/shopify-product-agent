from __future__ import annotations

from typing import Any

from manager.result_handler import AgentResult

SUPPORTED_ACTIONS = {
    "generate_image",
    "edit_image",
    "remove_background",
}


def handle_image_task(*, action: str, **_: Any) -> AgentResult:
    """Manager-facing Image Agent boundary.

    The creative image backend is intentionally not hard-coded here yet. This
    keeps routing and result contracts stable while the generation/editing
    backend is connected in the next Image Agent milestone.
    """
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"Unsupported Image Agent action: {action}")

    return AgentResult(
        agent="image_agent",
        task_id="",
        status="needs_input",
        summary=f"Image Agent action '{action}' is recognized but its creative backend is not connected yet.",
        errors=["Image generation/editing backend is not configured."],
    )
