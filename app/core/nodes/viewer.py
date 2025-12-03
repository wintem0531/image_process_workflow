"""查看器节点"""
from typing import Dict, Any

from app.core.nodes.base import BaseNode, NodeContext


class ImageViewerNode(BaseNode):
    """图像查看器节点"""

    @property
    def node_type(self) -> str:
        return "ImageViewer"

    @property
    def name(self) -> str:
        return "图像查看器"

    @property
    def description(self) -> str:
        return "显示图像（用于预览）"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像（透传）"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        # 透传图像
        return {"image": image}

    def get_code_template(self, context: NodeContext) -> str:
        return """# 图像查看器（透传）
# 图像已通过输入传递
"""


class DiffViewerNode(BaseNode):
    """差异查看器节点"""

    @property
    def node_type(self) -> str:
        return "DiffViewer"

    @property
    def name(self) -> str:
        return "差异查看器"

    @property
    def description(self) -> str:
        return "比较两张图像的差异"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image1": "第一张图像", "image2": "第二张图像"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"diff": "差异图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        import cv2
        import numpy as np

        image1 = context.inputs.get("image1")
        image2 = context.inputs.get("image2")
        if image1 is None or image2 is None:
            raise ValueError("缺少输入图像")

        # 确保尺寸一致
        if image1.shape != image2.shape:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))

        # 计算差异
        diff = cv2.absdiff(image1, image2)
        return {"diff": diff}

    def get_code_template(self, context: NodeContext) -> str:
        return """# 差异查看器
# 确保尺寸一致
if image1.shape != image2.shape:
    image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
diff = cv2.absdiff(image1, image2)
"""

