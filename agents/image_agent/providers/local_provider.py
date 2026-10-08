from __future__ import annotations

from pathlib import Path
from typing import Any

DEFAULT_GENERATION_MODEL = "runwayml/stable-diffusion-v1-5"


class LocalImageProvider:
    """Local, API-free Image Agent provider with lazy model loading."""

    def __init__(self, model_id: str = DEFAULT_GENERATION_MODEL) -> None:
        self.model_id = model_id
        self._text_pipe: Any = None
        self._edit_pipe: Any = None
        self._rembg_session: Any = None

    @staticmethod
    def _torch_device() -> tuple[Any, Any]:
        try:
            import torch
        except ImportError as exc:
            raise RuntimeError(
                "Local image generation needs PyTorch. Install requirements-local.txt."
            ) from exc
        if not torch.cuda.is_available():
            return torch, torch.float32
        return torch, torch.float16

    def _load_text_pipeline(self) -> Any:
        if self._text_pipe is not None:
            return self._text_pipe
        try:
            from diffusers import StableDiffusionPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Local image generation needs Diffusers. Install requirements-local.txt."
            ) from exc
        torch, dtype = self._torch_device()
        pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id, torch_dtype=dtype, safety_checker=None
        )
        if torch.cuda.is_available():
            pipe.enable_model_cpu_offload()
            pipe.enable_attention_slicing()
        else:
            pipe.to("cpu")
        self._text_pipe = pipe
        return pipe

    def _load_edit_pipeline(self) -> Any:
        if self._edit_pipe is not None:
            return self._edit_pipe
        try:
            from diffusers import StableDiffusionImg2ImgPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Local image editing needs Diffusers. Install requirements-local.txt."
            ) from exc
        torch, dtype = self._torch_device()
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            self.model_id, torch_dtype=dtype, safety_checker=None
        )
        if torch.cuda.is_available():
            pipe.enable_model_cpu_offload()
            pipe.enable_attention_slicing()
        else:
            pipe.to("cpu")
        self._edit_pipe = pipe
        return pipe

    def generate(self, *, prompt: str, output_path: str | Path,
                 width: int = 512, height: int = 512, steps: int = 20,
                 guidance_scale: float = 7.0) -> Path:
        if not prompt.strip():
            raise ValueError("An image generation prompt is required.")
        if width % 8 or height % 8:
            raise ValueError("Width and height must be divisible by 8.")
        pipe = self._load_text_pipeline()
        image = pipe(
            prompt=prompt, width=width, height=height,
            num_inference_steps=steps, guidance_scale=guidance_scale,
        ).images[0]
        return self._save(image, output_path)

    def edit(self, *, prompt: str, input_path: str | Path,
             output_path: str | Path, strength: float = 0.55,
             steps: int = 20) -> Path:
        if not prompt.strip():
            raise ValueError("An image edit prompt is required.")
        source = Path(input_path)
        if not source.is_file():
            raise ValueError(f"Input image does not exist: {source}")
        if not 0 < strength <= 1:
            raise ValueError("Edit strength must be greater than 0 and at most 1.")
        from PIL import Image
        pipe = self._load_edit_pipeline()
        image = Image.open(source).convert("RGB")
        image.thumbnail((768, 768))
        result = pipe(
            prompt=prompt, image=image, strength=strength,
            num_inference_steps=steps,
        ).images[0]
        return self._save(result, output_path)

    def remove_background(self, *, input_path: str | Path,
                          output_path: str | Path) -> Path:
        source = Path(input_path)
        if not source.is_file():
            raise ValueError(f"Input image does not exist: {source}")
        try:
            from rembg import new_session, remove
        except ImportError as exc:
            raise RuntimeError(
                "Local background removal needs rembg. Install requirements-local.txt."
            ) from exc
        if self._rembg_session is None:
            self._rembg_session = new_session("u2net")
        from PIL import Image
        image = Image.open(source).convert("RGBA")
        result = remove(image, session=self._rembg_session)
        return self._save(result, output_path)

    @staticmethod
    def _save(image: Any, output_path: str | Path) -> Path:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination)
        return destination
