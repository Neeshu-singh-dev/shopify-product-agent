from pathlib import Path

import pytest

from agents.image_agent.providers.local_provider import LocalImageProvider


def test_local_provider_validates_generation_prompt(tmp_path: Path):
    provider = LocalImageProvider()
    with pytest.raises(ValueError, match="prompt"):
        provider.generate(prompt="", output_path=tmp_path / "image.png")


def test_local_provider_validates_edit_input(tmp_path: Path):
    provider = LocalImageProvider()
    with pytest.raises(ValueError, match="Input image does not exist"):
        provider.edit(
            prompt="make it premium", input_path=tmp_path / "missing.png",
            output_path=tmp_path / "out.png",
        )


def test_local_provider_validates_edit_strength(tmp_path: Path):
    from PIL import Image
    source = tmp_path / "source.png"
    Image.new("RGB", (64, 64), "white").save(source)
    provider = LocalImageProvider()
    with pytest.raises(ValueError, match="Edit strength"):
        provider.edit(
            prompt="make it premium", input_path=source,
            output_path=tmp_path / "out.png", strength=0,
        )
