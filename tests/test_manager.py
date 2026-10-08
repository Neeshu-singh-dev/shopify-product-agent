from pathlib import Path

from manager.manager import Manager
from manager.planner import Planner


def test_planner_routes_image_optimization_to_product_agent():
    plan = Planner().plan("Optimize the product images in this folder")
    assert len(plan) == 1
    assert plan[0].agent == "product_agent"
    assert plan[0].action == "optimize_product_images"


def test_manager_can_register_and_execute_agent(tmp_path: Path):
    manager = Manager()

    def fake_agent(*, action, **kwargs):
        assert action == "optimize_product_images"
        assert kwargs["root"] == str(tmp_path)
        return {"ok": True}

    manager.register_agent("product_agent", "test product agent", fake_agent)
    results = manager.handle("Optimize these product images", root=str(tmp_path))

    assert len(results) == 1
    assert results[0].status == "success"
    assert results[0].agent == "product_agent"


def test_manager_reports_unrecognized_request():
    manager = Manager()
    results = manager.handle("Tell me something unrelated")
    assert results[0].status == "needs_input"
