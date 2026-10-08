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


def test_planner_preserves_combined_image_and_csv_workflow():
    plan = Planner().plan("Create product images and prepare the CSV")
    assert [(step.agent, step.action) for step in plan] == [
        ("image_agent", "creative_image_work"),
        ("product_agent", "prepare_product_assets"),
    ]


def test_manager_routes_generate_image_to_image_agent():
    manager = __import__("manager.manager", fromlist=["create_default_manager"]).create_default_manager()
    results = manager.handle("Create image for this product")

    assert len(results) == 1
    assert results[0].agent == "image_agent"
    assert results[0].status == "needs_input"
    assert results[0].task_id


def test_executor_assigns_task_id_to_specialist_result():
    manager = Manager()

    def specialist(*, action, **kwargs):
        from manager.result_handler import AgentResult
        return AgentResult(agent="product_agent", task_id="", status="success")

    manager.register_agent("product_agent", "test", specialist)
    results = manager.handle("Optimize product images", root="unused")

    assert results[0].task_id
