from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanStep:
    agent: str
    action: str


class Planner:
    """Small deterministic planner for the first Manager milestone."""

    def plan(self, request: str) -> list[PlanStep]:
        text = request.lower()

        # Combined workflows are checked first so a broad keyword such as
        # "optimize" cannot swallow a future multi-agent product workflow.
        if "product images" in text and "csv" in text:
            return [
                PlanStep("image_agent", "creative_image_work"),
                PlanStep("product_agent", "prepare_product_assets"),
            ]

        if any(term in text for term in ("generate image", "create image", "edit image", "remove background")):
            action = "remove_background" if "remove background" in text else ("edit_image" if "edit image" in text else "generate_image")
            return [PlanStep("image_agent", action)]

        if any(term in text for term in ("optimize", "webp", "resize", "compress", "rename", "organize")):
            return [PlanStep("product_agent", "optimize_product_images")]

        return []
