"""绘制节点"""
import cv2
import numpy as np
from typing import Dict, Any, List

from app.core.nodes.base import BaseNode, NodeContext


class DrawRectangleNode(BaseNode):
    """绘制矩形节点"""

    @property
    def node_type(self) -> str:
        return "DrawRectangle"

    @property
    def name(self) -> str:
        return "绘制矩形"

    @property
    def description(self) -> str:
        return "在图像上绘制矩形框"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像", "rects": "矩形列表（JSON，可选）"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X坐标", "default": 0},
                "y": {"type": "integer", "description": "Y坐标", "default": 0},
                "width": {"type": "integer", "description": "宽度", "default": 100},
                "height": {"type": "integer", "description": "高度", "default": 100},
                "color": {"type": "string", "description": "颜色（RGB，逗号分隔）", "default": "0,255,0"},
                "thickness": {"type": "integer", "description": "线宽", "default": 2},
            },
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        result = image.copy()
        
        # 获取绘制参数
        color_str = context.params.get("color", "0,255,0")
        thickness = context.params.get("thickness", 2)
        try:
            color = tuple(map(int, color_str.split(",")))
        except:
            color = (0, 255, 0)

        # 优先使用输入的rects，否则使用参数
        rects = context.inputs.get("rects")
        if rects:
            # 处理不同格式的rects输入
            for rect in rects:
                if isinstance(rect, dict):
                    # 标准矩形格式 {"x": 0, "y": 0, "width": 100, "height": 100}
                    x = rect.get("x", 0)
                    y = rect.get("y", 0)
                    w = rect.get("width", 100)
                    h = rect.get("height", 100)
                    cv2.rectangle(result, (x, y), (x + w, y + h), color, thickness)
                elif isinstance(rect, (list, tuple)):
                    # 轮廓点列表格式 [[x1,y1], [x2,y2], ...]
                    # 计算外接矩形
                    points = np.array(rect, dtype=np.int32)
                    if len(points) > 0:
                        x, y, w, h = cv2.boundingRect(points)
                        cv2.rectangle(result, (x, y), (x + w, y + h), color, thickness)
        else:
            # 使用参数绘制单个矩形
            x = context.params.get("x", 0)
            y = context.params.get("y", 0)
            w = context.params.get("width", 100)
            h = context.params.get("height", 100)
            cv2.rectangle(result, (x, y), (x + w, y + h), color, thickness)

        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        x = context.params.get("x", 0)
        y = context.params.get("y", 0)
        w = context.params.get("width", 100)
        h = context.params.get("height", 100)
        color = context.params.get("color", "0,255,0")
        thickness = context.params.get("thickness", 2)
        return f"""# 绘制矩形
result = image.copy()
color = ({color})
cv2.rectangle(result, ({x}, {y}), ({x+w}, {y+h}), color, {thickness})
"""


class DrawTextNode(BaseNode):
    """绘制文本节点"""

    @property
    def node_type(self) -> str:
        return "DrawText"

    @property
    def name(self) -> str:
        return "绘制文本"

    @property
    def description(self) -> str:
        return "在图像上绘制文本"

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
                "text": {"type": "string", "description": "文本内容", "default": "Text"},
                "x": {"type": "integer", "description": "X坐标", "default": 10},
                "y": {"type": "integer", "description": "Y坐标", "default": 30},
                "font": {
                    "type": "string",
                    "enum": ["FONT_HERSHEY_SIMPLEX", "FONT_HERSHEY_PLAIN", "FONT_HERSHEY_DUPLEX"],
                    "default": "FONT_HERSHEY_SIMPLEX",
                },
                "font_scale": {"type": "number", "description": "字体大小", "default": 1.0},
                "color": {"type": "string", "description": "颜色（RGB）", "default": "255,255,255"},
                "thickness": {"type": "integer", "description": "线宽", "default": 1},
            },
            "required": ["text"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        text = context.params.get("text", "Text")
        x = context.params.get("x", 10)
        y = context.params.get("y", 30)
        font = getattr(cv2, context.params.get("font", "FONT_HERSHEY_SIMPLEX"))
        font_scale = context.params.get("font_scale", 1.0)
        color_str = context.params.get("color", "255,255,255")
        thickness = context.params.get("thickness", 1)
        color = tuple(map(int, color_str.split(",")))

        result = image.copy()
        cv2.putText(result, text, (x, y), font, font_scale, color, thickness)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        text = context.params.get("text", "Text")
        x = context.params.get("x", 10)
        y = context.params.get("y", 30)
        font = context.params.get("font", "FONT_HERSHEY_SIMPLEX")
        font_scale = context.params.get("font_scale", 1.0)
        color = context.params.get("color", "255,255,255")
        thickness = context.params.get("thickness", 1)
        return f"""# 绘制文本
result = image.copy()
color = ({color})
cv2.putText(result, "{text}", ({x}, {y}), cv2.{font}, {font_scale}, color, {thickness})
"""


class OverlayNode(BaseNode):
    """图层合成节点"""

    @property
    def node_type(self) -> str:
        return "Overlay"

    @property
    def name(self) -> str:
        return "图层合成"

    @property
    def description(self) -> str:
        return "将两张图像按图层合成"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image1": "底层图像", "image2": "上层图像"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "alpha": {"type": "number", "description": "透明度（0-1）", "default": 0.5},
                "x": {"type": "integer", "description": "上层图像X偏移", "default": 0},
                "y": {"type": "integer", "description": "上层图像Y偏移", "default": 0},
            },
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image1 = context.inputs.get("image1")
        image2 = context.inputs.get("image2")
        if image1 is None or image2 is None:
            raise ValueError("缺少输入图像")

        alpha = context.params.get("alpha", 0.5)
        x = context.params.get("x", 0)
        y = context.params.get("y", 0)

        # 确保图像尺寸一致
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]

        # 调整image2大小以适应image1
        if h2 != h1 or w2 != w1:
            image2_resized = cv2.resize(image2, (w1, h1))
        else:
            image2_resized = image2

        # 合成
        result = cv2.addWeighted(image1, 1 - alpha, image2_resized, alpha, 0)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        alpha = context.params.get("alpha", 0.5)
        return f"""# 图层合成
result = cv2.addWeighted(image1, {1-alpha}, image2, {alpha}, 0)
"""

