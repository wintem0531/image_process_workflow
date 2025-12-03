"""几何/轮廓节点"""
import cv2
import numpy as np
from typing import Dict, Any, List

from app.core.nodes.base import BaseNode, NodeContext


class FindContoursNode(BaseNode):
    """查找轮廓节点"""

    @property
    def node_type(self) -> str:
        return "FindContours"

    @property
    def name(self) -> str:
        return "查找轮廓"

    @property
    def description(self) -> str:
        return "查找图像中的轮廓"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像（二值图）"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"contours": "轮廓列表（JSON）", "image": "绘制轮廓后的图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["RETR_EXTERNAL", "RETR_LIST", "RETR_CCOMP", "RETR_TREE"],
                    "default": "RETR_EXTERNAL",
                },
                "method": {
                    "type": "string",
                    "enum": ["CHAIN_APPROX_NONE", "CHAIN_APPROX_SIMPLE", "CHAIN_APPROX_TC89_L1", "CHAIN_APPROX_TC89_KCOS"],
                    "default": "CHAIN_APPROX_SIMPLE",
                },
            },
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        image = context.inputs.get("image")
        if image is None:
            raise ValueError("缺少输入图像")

        # 确保输入是单通道灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        mode = getattr(cv2, context.params.get('mode', 'RETR_EXTERNAL'))
        method = getattr(cv2, context.params.get('method', 'CHAIN_APPROX_SIMPLE'))

        contours, hierarchy = cv2.findContours(gray, mode, method)
        
        # 转换为可序列化的格式
        contours_json = []
        for contour in contours:
            points = contour.reshape(-1, 2).tolist()
            contours_json.append(points)

        # 绘制轮廓（在彩色图上）
        if len(image.shape) == 2:
            result_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        else:
            result_image = image.copy()
        cv2.drawContours(result_image, contours, -1, (0, 255, 0), 2)

        return {
            "contours": contours_json,
            "image": result_image,
        }

    def get_code_template(self, context: NodeContext) -> str:
        mode = context.params.get("mode", "RETR_EXTERNAL")
        method = context.params.get("method", "CHAIN_APPROX_SIMPLE")
        return f"""# 查找轮廓
contours, hierarchy = cv2.findContours(image, cv2.{mode}, cv2.{method})
# 绘制轮廓
result = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR) if len(image.shape) == 2 else image.copy()
cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
"""


class BoundingRectNode(BaseNode):
    """外接矩形节点"""

    @property
    def node_type(self) -> str:
        return "BoundingRect"

    @property
    def name(self) -> str:
        return "外接矩形"

    @property
    def description(self) -> str:
        return "计算轮廓的外接矩形"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"contours": "轮廓列表（JSON）"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"rects": "矩形列表（JSON）", "image": "绘制矩形后的图像（如果提供输入图像）"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "可选：输入图像（用于绘制）", "default": ""},
            },
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        contours = context.inputs.get("contours")
        if contours is None:
            raise ValueError("缺少输入轮廓")

        # 将JSON轮廓转换为numpy数组
        contours_np = []
        for contour in contours:
            contours_np.append(np.array(contour, dtype=np.int32))

        # 计算外接矩形
        rects = []
        for contour in contours_np:
            x, y, w, h = cv2.boundingRect(contour)
            rects.append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})

        result = {"rects": rects}

        # 如果有输入图像，绘制矩形
        input_image = context.inputs.get("image")
        if input_image is not None:
            result_image = input_image.copy()
            for rect in rects:
                x, y, w, h = rect["x"], rect["y"], rect["width"], rect["height"]
                cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            result["image"] = result_image

        return result

    def get_code_template(self, context: NodeContext) -> str:
        return """# 计算外接矩形
rects = []
for contour in contours:
    x, y, w, h = cv2.boundingRect(contour)
    rects.append({"x": x, "y": y, "width": w, "height": h})
"""


class MinAreaRectNode(BaseNode):
    """最小外接矩形节点"""

    @property
    def node_type(self) -> str:
        return "MinAreaRect"

    @property
    def name(self) -> str:
        return "最小外接矩形"

    @property
    def description(self) -> str:
        return "计算轮廓的最小外接旋转矩形"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"contours": "轮廓列表（JSON）"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"rects": "旋转矩形列表（JSON）"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        contours = context.inputs.get("contours")
        if contours is None:
            raise ValueError("缺少输入轮廓")

        # 将JSON轮廓转换为numpy数组
        contours_np = []
        for contour in contours:
            contours_np.append(np.array(contour, dtype=np.int32))

        # 计算最小外接矩形
        rects = []
        for contour in contours_np:
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            rects.append({
                "center": {"x": float(rect[0][0]), "y": float(rect[0][1])},
                "size": {"width": float(rect[1][0]), "height": float(rect[1][1])},
                "angle": float(rect[2]),
                "box": box.tolist(),
            })

        return {"rects": rects}

    def get_code_template(self, context: NodeContext) -> str:
        return """# 计算最小外接矩形
rects = []
for contour in contours:
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    rects.append({
        "center": rect[0],
        "size": rect[1],
        "angle": rect[2],
        "box": box.tolist(),
    })
"""

