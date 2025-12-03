"""节点测试"""
import pytest
import numpy as np
import cv2
from app.core.nodes.base import NodeContext
from app.core.nodes.image_input import ImageInputNode
from app.core.nodes.image_process import ResizeNode, GrayscaleNode, ThresholdNode
from app.core.nodes.morphology import ErodeNode, DilateNode


@pytest.fixture
def sample_image():
    """创建测试图像"""
    return np.ones((100, 100, 3), dtype=np.uint8) * 255


@pytest.mark.asyncio
async def test_resize_node(sample_image):
    """测试调整大小节点"""
    node = ResizeNode()
    context = NodeContext(
        node_id="test",
        inputs={"image": sample_image},
        params={"width": 50, "height": 50},
        input_data={},
    )
    result = await node.execute(context)
    assert "image" in result
    assert result["image"].shape == (50, 50, 3)


@pytest.mark.asyncio
async def test_grayscale_node(sample_image):
    """测试灰度化节点"""
    node = GrayscaleNode()
    context = NodeContext(
        node_id="test",
        inputs={"image": sample_image},
        params={},
        input_data={},
    )
    result = await node.execute(context)
    assert "image" in result
    assert len(result["image"].shape) == 2


@pytest.mark.asyncio
async def test_threshold_node(sample_image):
    """测试二值化节点"""
    # 先转换为灰度图
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    
    node = ThresholdNode()
    context = NodeContext(
        node_id="test",
        inputs={"image": gray},
        params={"threshold": 127, "max_value": 255},
        input_data={},
    )
    result = await node.execute(context)
    assert "image" in result
    assert len(result["image"].shape) == 2


@pytest.mark.asyncio
async def test_erode_node(sample_image):
    """测试腐蚀节点"""
    # 创建二值图像
    binary = np.zeros((100, 100), dtype=np.uint8)
    binary[40:60, 40:60] = 255
    
    node = ErodeNode()
    context = NodeContext(
        node_id="test",
        inputs={"image": binary},
        params={"kernel_size": 3, "iterations": 1},
        input_data={},
    )
    result = await node.execute(context)
    assert "image" in result
    assert result["image"].shape == binary.shape


@pytest.mark.asyncio
async def test_dilate_node(sample_image):
    """测试膨胀节点"""
    # 创建二值图像
    binary = np.zeros((100, 100), dtype=np.uint8)
    binary[40:60, 40:60] = 255
    
    node = DilateNode()
    context = NodeContext(
        node_id="test",
        inputs={"image": binary},
        params={"kernel_size": 3, "iterations": 1},
        input_data={},
    )
    result = await node.execute(context)
    assert "image" in result
    assert result["image"].shape == binary.shape

