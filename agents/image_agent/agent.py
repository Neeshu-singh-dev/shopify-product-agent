from __future__ import annotations

from pathlib import Path
from typing import Any

from manager.result_handler import AgentResult

SUPPORTED_ACTIONS = {
    "generate_image",
    "edit_image",
    "remove_background",
}


def handle_image_task(*, action: str, prompt: str = "", input_path: str | Path | None = None,
                      output_path: str | Path | None = None, model: str | None = None,
                      size: str = "1024x1024", quality: str = "high",
                      background: str = "auto", output_format: str = "png",
                      **_: Any) -> AgentResult:
    """Manager-facing Image Agent backed by the OpenAI Images API."""
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"Unsupported Image Agent action: {action}")

    if action == "generate_image":
        if not prompt.strip():
            return AgentResult(
                agent="image_agent",
                task_id="",
                status="needs_input",
                summary="Image generation requires a prompt.",
                errors=["Missing prompt."],
            )
        if not output_path:
            return AgentResult(
                agent="image_agent",
                task_id="",
                status="needs_input",
                summary="Image generation requires an output path.",
                errors=["Missing output_path."],
            )

        from .backend import generate_image
        path = generate_image(
            prompt=prompt,
            output_path=output_path,
            model=model or "gpt-image-2.5-sunburst",
            size=size,
            quality=quality,
            background=background,
        )
    elif action == "edit_image":
        if not prompt.strip() or not input_path or not output_path:
            return AgentResult(
                agent="image_agent",
                task_id="",
                status="needs_input",
                summary="Image editing requires a prompt, input image, and output path.",
                errors=["Missing prompt, input_path, or output_path."],
            )

        from .backend import edit_image
        path = edit_image(
            prompt=prompt,
            input_path=input_path,
            output_path=output_path,
            model=model or "gpt-image-2.5-sunburst",
            size=size if size != "1024x1024" else "auto",
            quality=quality,
            background=background,
            output_format=output_format,
        )
    else:
        if not input_path or not output_path:
            return AgentResult(
                agent="image_agent",
                task_id="",
                status="needs_input",
                summary="Background removal requires an input image and output path.",
                errors=["Missing input_path or output_path."],
            )

        from .backend import remove_background
        path = remove_background(
            input_path=input_path,
            output_path=output_path,
            model=model or "gpt-image-2.5-sunburst",
        )

    return AgentResult(
        agent="image_agent",
        task_id="",
        status="success",
        summary=f"Image Agent completed {action}.",
        outputs=[str(path)],
        statistics={"output_path": str(path), "model": model or "gpt-image-2.5-sunburst"},
    )
