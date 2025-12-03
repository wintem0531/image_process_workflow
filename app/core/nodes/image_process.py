"""基本图像处理节点"""
import cv2
import numpy as np
from typing import Dict, Any

from app.core.nodes.base import BaseNode, NodeContext


class ResizeNode(BaseNode):
    """调整大小节点"""

    @property
    def node_type(self) -> str:
        return "Resize"

    @property
    def name(self) -> str:
        return "调整大小"

    @property
    def description(self) -> str:
        return "调整图像尺寸"

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
                "width": {"type": "integer", "description": "宽度", "default": 640},
                "height": {"type": "integer", "description": "高度", "default": 480},
                "interpolation": {
                    "type": "string",
                    "enum": ["INTER_LINEAR", "INTER_NEAREST", "INTER_CUBIC", "INTER_AREA"],
                    "default": "INTER_LINEAR",
                },
            },
            "required": ["width", "height"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        width = context.params.get("width", 640)
        height = context.params.get("height", 480)
        interpolation = getattr(cv2, context.params.get("interpolation", "INTER_LINEAR"))

        result = cv2.resize(image, (width, height), interpolation=interpolation)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        width = context.params.get("width", 640)
        height = context.params.get("height", 480)
        interpolation = context.params.get("interpolation", "INTER_LINEAR")
        return f"""# 调整图像大小
result = cv2.resize(image, ({width}, {height}), interpolation=cv2.{interpolation})
"""


class CropNode(BaseNode):
    """裁剪节点"""

    @property
    def node_type(self) -> str:
        return "Crop"

    @property
    def name(self) -> str:
        return "裁剪"

    @property
    def description(self) -> str:
        return "裁剪图像区域"

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
                "x": {"type": "integer", "description": "左上角X坐标", "default": 0},
                "y": {"type": "integer", "description": "左上角Y坐标", "default": 0},
                "width": {"type": "integer", "description": "宽度", "default": 100},
                "height": {"type": "integer", "description": "高度", "default": 100},
            },
            "required": ["x", "y", "width", "height"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        x = context.params.get("x", 0)
        y = context.params.get("y", 0)
        w = context.params.get("width", 100)
        h = context.params.get("height", 100)

        result = image[y:y+h, x:x+w]
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        x = context.params.get("x", 0)
        y = context.params.get("y", 0)
        w = context.params.get("width", 100)
        h = context.params.get("height", 100)
        return f"""# 裁剪图像
result = image[{y}:{y+h}, {x}:{x+w}]
"""


class GrayscaleNode(BaseNode):
    """灰度化节点"""

    @property
    def node_type(self) -> str:
        return "Grayscale"

    @property
    def name(self) -> str:
        return "灰度化"

    @property
    def description(self) -> str:
        return "将图像转换为灰度图"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        if len(image.shape) == 2:
            result = image
        else:
            result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        return """# 转换为灰度图
if len(image.shape) == 3:
    result = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
else:
    result = image
"""


class ThresholdNode(BaseNode):
    """二值化节点"""

    @property
    def node_type(self) -> str:
        return "Threshold"

    @property
    def name(self) -> str:
        return "二值化"

    @property
    def description(self) -> str:
        return "图像二值化处理"

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
                "threshold": {"type": "number", "description": "阈值", "default": 127},
                "max_value": {"type": "number", "description": "最大值", "default": 255},
                "type": {
                    "type": "string",
                    "enum": ["THRESH_BINARY", "THRESH_BINARY_INV", "THRESH_TRUNC", "THRESH_TOZERO", "THRESH_TOZERO_INV"],
                    "default": "THRESH_BINARY",
                },
            },
            "required": ["threshold"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        threshold = context.params.get("threshold", 127)
        max_value = context.params.get("max_value", 255)
        thresh_type = getattr(cv2, context.params.get("type", "THRESH_BINARY"))

        _, result = cv2.threshold(image, threshold, max_value, thresh_type)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        threshold = context.params.get("threshold", 127)
        max_value = context.params.get("max_value", 255)
        thresh_type = context.params.get("type", "THRESH_BINARY")
        return f"""# 二值化
_, result = cv2.threshold(image, {threshold}, {max_value}, cv2.{thresh_type})
"""


class BlurNode(BaseNode):
    """模糊节点"""

    @property
    def node_type(self) -> str:
        return "Blur"

    @property
    def name(self) -> str:
        return "模糊"

    @property
    def description(self) -> str:
        return "图像模糊处理"

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
                "kernel_size": {"type": "integer", "description": "核大小（奇数）", "default": 5},
            },
            "required": ["kernel_size"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        kernel_size = context.params.get("kernel_size", 5)
        result = cv2.blur(image, (kernel_size, kernel_size))
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        kernel_size = context.params.get("kernel_size", 5)
        return f"""# 模糊处理
result = cv2.blur(image, ({kernel_size}, {kernel_size}))
"""


class GaussianBlurNode(BaseNode):
    """高斯模糊节点"""

    @property
    def node_type(self) -> str:
        return "GaussianBlur"

    @property
    def name(self) -> str:
        return "高斯模糊"

    @property
    def description(self) -> str:
        return "高斯模糊处理"

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
                "kernel_size": {"type": "integer", "description": "核大小（奇数）", "default": 5},
                "sigma_x": {"type": "number", "description": "X方向标准差", "default": 0},
                "sigma_y": {"type": "number", "description": "Y方向标准差", "default": 0},
            },
            "required": ["kernel_size"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        kernel_size = context.params.get("kernel_size", 5)
        sigma_x = context.params.get("sigma_x", 0)
        sigma_y = context.params.get("sigma_y", 0)

        result = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma_x, sigma_y)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        kernel_size = context.params.get("kernel_size", 5)
        sigma_x = context.params.get("sigma_x", 0)
        sigma_y = context.params.get("sigma_y", 0)
        return f"""# 高斯模糊
result = cv2.GaussianBlur(image, ({kernel_size}, {kernel_size}), {sigma_x}, {sigma_y})
"""

