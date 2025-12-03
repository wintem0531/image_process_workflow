"""形态学操作节点"""
import cv2
import numpy as np
from typing import Dict, Any

from app.core.nodes.base import BaseNode, NodeContext


class ErodeNode(BaseNode):
    """腐蚀节点"""

    @property
    def node_type(self) -> str:
        return "Erode"

    @property
    def name(self) -> str:
        return "腐蚀"

    @property
    def description(self) -> str:
        return "形态学腐蚀操作"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "kernel_size": {"type": "integer", "description": "核大小", "default": 3},
                "iterations": {"type": "integer", "description": "迭代次数", "default": 1},
            },
            "required": ["kernel_size"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        kernel_size = context.params.get("kernel_size", 3)
        iterations = context.params.get("iterations", 1)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        result = cv2.erode(image, kernel, iterations=iterations)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        kernel_size = context.params.get("kernel_size", 3)
        iterations = context.params.get("iterations", 1)
        return f"""# 腐蚀操作
kernel = np.ones(({kernel_size}, {kernel_size}), np.uint8)
result = cv2.erode(image, kernel, iterations={iterations})
"""


class DilateNode(BaseNode):
    """膨胀节点"""

    @property
    def node_type(self) -> str:
        return "Dilate"

    @property
    def name(self) -> str:
        return "膨胀"

    @property
    def description(self) -> str:
        return "形态学膨胀操作"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "kernel_size": {"type": "integer", "description": "核大小", "default": 3},
                "iterations": {"type": "integer", "description": "迭代次数", "default": 1},
            },
            "required": ["kernel_size"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        kernel_size = context.params.get("kernel_size", 3)
        iterations = context.params.get("iterations", 1)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        result = cv2.dilate(image, kernel, iterations=iterations)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        kernel_size = context.params.get("kernel_size", 3)
        iterations = context.params.get("iterations", 1)
        return f"""# 膨胀操作
kernel = np.ones(({kernel_size}, {kernel_size}), np.uint8)
result = cv2.dilate(image, kernel, iterations={iterations})
"""


class OpenNode(BaseNode):
    """开运算节点"""

    @property
    def node_type(self) -> str:
        return "Open"

    @property
    def name(self) -> str:
        return "开运算"

    @property
    def description(self) -> str:
        return "形态学开运算（先腐蚀后膨胀）"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "kernel_size": {"type": "integer", "description": "核大小", "default": 3},
            },
            "required": ["kernel_size"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        kernel_size = context.params.get("kernel_size", 3)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        kernel_size = context.params.get("kernel_size", 3)
        return f"""# 开运算
kernel = np.ones(({kernel_size}, {kernel_size}), np.uint8)
result = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
"""


class CloseNode(BaseNode):
    """闭运算节点"""

    @property
    def node_type(self) -> str:
        return "Close"

    @property
    def name(self) -> str:
        return "闭运算"

    @property
    def description(self) -> str:
        return "形态学闭运算（先膨胀后腐蚀）"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "kernel_size": {"type": "integer", "description": "核大小", "default": 3},
            },
            "required": ["kernel_size"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        kernel_size = context.params.get("kernel_size", 3)
        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        kernel_size = context.params.get("kernel_size", 3)
        return f"""# 闭运算
kernel = np.ones(({kernel_size}, {kernel_size}), np.uint8)
result = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
"""

