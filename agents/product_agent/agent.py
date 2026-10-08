from __future__ import annotations

from pathlib import Path
from typing import Any

from app.image_engine import optimize_root
from manager.result_handler import AgentResult


def handle_product_task(*, action: str, root: str | Path, quality: int = 88,
                        max_width: int = 2000, max_height: int = 2000, **_: Any) -> AgentResult:
    """Stable Manager-facing adapter around the existing V1 image engine."""
    if action != "optimize_product_images":
        raise ValueError(f"Unsupported Product Agent action: {action}")

    root_path = Path(root)
    if not root_path.is_dir():
        raise ValueError(f"Product root does not exist: {root_path}")

    report, _rows, summary = optimize_root(root_path, quality, max_width, max_height)
    return AgentResult(
        agent="product_agent",
        task_id="",
        status="success" if summary["failed"] == 0 else "completed_with_errors",
        summary=(
            f"Processed {summary['images_found']} images; "
            f"{summary['converted']} converted, {summary['gif_unchanged']} GIF unchanged, "
            f"{summary['failed']} failed."
        ),
        outputs=[str(report)],
        statistics=summary,
    )
