from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any


DEFAULT_MODEL = "gpt-image-2.5-sunburst"
SUPPORTED_ACTIONS = {"generate_image", "edit_image", "remove_background"}


def _client():
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The OpenAI Python package is not installed. Install it with: "
            "python -m pip install openai"
        ) from exc

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    return OpenAI()


def _save_result(result: Any, output_path: Path) -> Path:
    if not result.data or not result.data[0].b64_json:
        raise RuntimeError("The image service returned no image data.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(result.data[0].b64_json))
    return output_path


def generate_image(*, prompt: str, output_path: str | Path,
                   model: str = DEFAULT_MODEL, size: str = "1024x1024",
                   quality: str = "high", background: str = "auto") -> Path:
    if not prompt.strip():
        raise ValueError("An image generation prompt is required.")

    result = _client().images.generate(
        model=model,
        prompt=prompt,
        n=1,
        size=size,
        quality=quality,
        background=background,
    )
    return _save_result(result, Path(output_path))


def edit_image(*, prompt: str, input_path: str | Path, output_path: str | Path,
               model: str = DEFAULT_MODEL, size: str = "auto",
               quality: str = "high", background: str = "auto",
               output_format: str = "png") -> Path:
    if not prompt.strip():
        raise ValueError("An image edit prompt is required.")

    source = Path(input_path)
    if not source.is_file():
        raise ValueError(f"Input image does not exist: {source}")

    result = _client().images.edit(
        model=model,
        image=open(source, "rb"),
        prompt=prompt,
        size=size,
        quality=quality,
        background=background,
        output_format=output_format,
    )
    return _save_result(result, Path(output_path))


def remove_background(*, input_path: str | Path, output_path: str | Path,
                      model: str = DEFAULT_MODEL) -> Path:
    return edit_image(
        prompt="Remove the background completely. Preserve the main subject exactly and keep clean natural edges.",
        input_path=input_path,
        output_path=output_path,
        model=model,
        background="transparent",
        output_format="png",
    )
