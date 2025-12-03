"""工作流测试"""
import pytest
from app.models.workflow import Workflow, Node, Link, NodePort
from app.core.workflow import WorkflowEngine
from app.core.nodes.registry import NodeRegistry


@pytest.fixture
def simple_workflow():
    """创建简单工作流"""
    return Workflow(
        workflow_id="test-workflow",
        name="测试工作流",
        nodes=[
            Node(
                id="n1",
                type="ImageInput",
                params={"path": "test.jpg"},
            ),
            Node(
                id="n2",
                type="Resize",
                params={"width": 100, "height": 100},
            ),
        ],
        links=[
            Link(
                from_=NodePort(node="n1", port="image"),
                to=NodePort(node="n2", port="image"),
            ),
        ],
    )


def test_build_graph(simple_workflow):
    """测试构建依赖图"""
    registry = NodeRegistry()
    registry.register_all()
    engine = WorkflowEngine(registry)
    
    graph = engine._build_graph(simple_workflow)
    assert "n1" in graph
    assert "n2" in graph
    assert "n1" in graph["n2"]["dependencies"]


def test_topological_sort(simple_workflow):
    """测试拓扑排序"""
    registry = NodeRegistry()
    registry.register_all()
    engine = WorkflowEngine(registry)
    
    graph = engine._build_graph(simple_workflow)
    order = engine._topological_sort(graph)
    assert order[0] == "n1"
    assert order[1] == "n2"

