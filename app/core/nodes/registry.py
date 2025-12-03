"""节点注册表"""
from typing import Dict, Type, List
from app.core.nodes.base import BaseNode
from app.core.nodes.image_input import ImageInputNode
from app.core.nodes.image_process import (
    ResizeNode,
    CropNode,
    GrayscaleNode,
    ThresholdNode,
    BlurNode,
    GaussianBlurNode,
)
from app.core.nodes.morphology import (
    ErodeNode,
    DilateNode,
    OpenNode,
    CloseNode,
)
from app.core.nodes.geometry import (
    FindContoursNode,
    BoundingRectNode,
    MinAreaRectNode,
)
from app.core.nodes.draw import (
    DrawRectangleNode,
    DrawTextNode,
    OverlayNode,
)
from app.core.nodes.concat import (
    ConcatHorizontalNode,
    ConcatVerticalNode,
    TileNode,
)
from app.core.nodes.data import JSONInputNode, JSONOutputNode
from app.core.nodes.viewer import ImageViewerNode, DiffViewerNode
from app.core.nodes.script import PythonSnippetNode


class NodeRegistry:
    """节点注册表"""

    def __init__(self):
        self._nodes: Dict[str, BaseNode] = {}

    def register(self, node_type: str, node_instance: BaseNode):
        """注册节点"""
        self._nodes[node_type] = node_instance

    def register_all(self):
        """注册所有内置节点"""
        nodes = [
            ImageInputNode(),
            ResizeNode(),
            CropNode(),
            GrayscaleNode(),
            ThresholdNode(),
            BlurNode(),
            GaussianBlurNode(),
            ErodeNode(),
            DilateNode(),
            OpenNode(),
            CloseNode(),
            FindContoursNode(),
            BoundingRectNode(),
            MinAreaRectNode(),
            DrawRectangleNode(),
            DrawTextNode(),
            OverlayNode(),
            ConcatHorizontalNode(),
            ConcatVerticalNode(),
            TileNode(),
            JSONInputNode(),
            JSONOutputNode(),
            ImageViewerNode(),
            DiffViewerNode(),
            PythonSnippetNode(),
        ]

        for node in nodes:
            self.register(node.node_type, node)

    def get(self, node_type: str) -> BaseNode:
        """获取节点实例"""
        if node_type not in self._nodes:
            raise ValueError(f"未知节点类型: {node_type}")
        return self._nodes[node_type]

    def list_all(self) -> List[Dict[str, any]]:
        """列出所有节点信息"""
        result = []
        for node_type, node in self._nodes.items():
            result.append({
                "type": node_type,
                "name": node.name,
                "description": node.description,
                "input_ports": node.input_ports,
                "output_ports": node.output_ports,
                "param_schema": node.param_schema,
            })
        return result

