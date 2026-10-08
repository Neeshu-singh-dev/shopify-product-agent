from __future__ import annotations

from pathlib import Path
from typing import Any

from manager.result_handler import AgentResult

SUPPORTED_ACTIONS = {"generate_image", "edit_image", "remove_background"}


def handle_image_task(*, action: str, prompt: str = "", input_path: str | Path | None = None,
                      output_path: str | Path | None = None, model: str | None = None,
                      size: str = "512x512", image_quality: str = "standard",
                      background: str = "auto", output_format: str = "png",
                      provider: str = "local", steps: int = 20,
                      strength: float = 0.55, **_: Any) -> AgentResult:
    """Manager-facing Image Agent using a local, API-free provider."""
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"Unsupported Image Agent action: {action}")
    if provider != "local":
        return AgentResult(
            agent="image_agent", task_id="", status="needs_input",
            summary=f"Image provider '{provider}' is not enabled. Jarvis is local-only.",
            errors=["Only the local provider is currently supported."],
        )

    from .providers.local_provider import DEFAULT_GENERATION_MODEL, LocalImageProvider

    local = LocalImageProvider(model_id=model or DEFAULT_GENERATION_MODEL)
    if action == "generate_image":
        if not prompt.strip() or not output_path:
            return AgentResult(
                agent="image_agent", task_id="", status="needs_input",
                summary="Image generation requires a prompt and output path.",
                errors=["Missing prompt or output_path."],
            )
        try:
            width, height = (int(part) for part in size.lower().split("x", 1))
        except ValueError as exc:
            raise ValueError("Local image size must use WIDTHxHEIGHT, for example 512x512.") from exc
        path = local.generate(
            prompt=prompt, output_path=output_path, width=width, height=height, steps=steps
        )
    elif action == "edit_image":
        if not prompt.strip() or not input_path or not output_path:
            return AgentResult(
                agent="image_agent", task_id="", status="needs_input",
                summary="Image editing requires a prompt, input image, and output path.",
                errors=["Missing prompt, input_path, or output_path."],
            )
        path = local.edit(
            prompt=prompt, input_path=input_path, output_path=output_path,
            strength=strength, steps=steps,
        )
    else:
        if not input_path or not output_path:
            return AgentResult(
                agent="image_agent", task_id="", status="needs_input",
                summary="Background removal requires an input image and output path.",
                errors=["Missing input_path or output_path."],
            )
        path = local.remove_background(input_path=input_path, output_path=output_path)

    return AgentResult(
        agent="image_agent", task_id="", status="success",
        summary=f"Local Image Agent completed {action}.",
        outputs=[str(path)],
        statistics={"output_path": str(path), "provider": "local", "model": local.model_id},
    )
