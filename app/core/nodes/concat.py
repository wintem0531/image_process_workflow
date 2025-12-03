"""拼接节点"""
import cv2
import numpy as np
from typing import Dict, Any, List

from app.core.nodes.base import BaseNode, NodeContext


class ConcatHorizontalNode(BaseNode):
    """水平拼接节点"""

    @property
    def node_type(self) -> str:
        return "ConcatHorizontal"

    @property
    def name(self) -> str:
        return "水平拼接"

    @property
    def description(self) -> str:
        return "将多张图像水平拼接"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"images": "图像列表"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        images = context.inputs.get("images")
        if images is None:
            raise ValueError("缺少输入图像")

        if not isinstance(images, list):
            images = [images]

        # 统一高度
        heights = [img.shape[0] for img in images]
        min_height = min(heights)
        images_resized = []
        for img in images:
            if img.shape[0] != min_height:
                scale = min_height / img.shape[0]
                new_width = int(img.shape[1] * scale)
                img_resized = cv2.resize(img, (new_width, min_height))
                images_resized.append(img_resized)
            else:
                images_resized.append(img)

        result = np.hstack(images_resized)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        return """# 水平拼接
# 统一高度
min_height = min(img.shape[0] for img in images)
images_resized = [cv2.resize(img, (int(img.shape[1] * min_height / img.shape[0]), min_height)) 
                  if img.shape[0] != min_height else img for img in images]
result = np.hstack(images_resized)
"""


class ConcatVerticalNode(BaseNode):
    """垂直拼接节点"""

    @property
    def node_type(self) -> str:
        return "ConcatVertical"

    @property
    def name(self) -> str:
        return "垂直拼接"

    @property
    def description(self) -> str:
        return "将多张图像垂直拼接"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"images": "图像列表"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        images = context.inputs.get("images")
        if images is None:
            raise ValueError("缺少输入图像")

        if not isinstance(images, list):
            images = [images]

        # 统一宽度
        widths = [img.shape[1] for img in images]
        min_width = min(widths)
        images_resized = []
        for img in images:
            if img.shape[1] != min_width:
                scale = min_width / img.shape[1]
                new_height = int(img.shape[0] * scale)
                img_resized = cv2.resize(img, (min_width, new_height))
                images_resized.append(img_resized)
            else:
                images_resized.append(img)

        result = np.vstack(images_resized)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        return """# 垂直拼接
# 统一宽度
min_width = min(img.shape[1] for img in images)
images_resized = [cv2.resize(img, (min_width, int(img.shape[0] * min_width / img.shape[1]))) 
                  if img.shape[1] != min_width else img for img in images]
result = np.vstack(images_resized)
"""


class TileNode(BaseNode):
    """平铺节点"""

    @property
    def node_type(self) -> str:
        return "Tile"

    @property
    def name(self) -> str:
        return "平铺"

    @property
    def description(self) -> str:
        return "将多张图像平铺成网格"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"images": "图像列表"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "cols": {"type": "integer", "description": "列数", "default": 3},
                "rows": {"type": "integer", "description": "行数", "default": 3},
            },
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        images = context.inputs.get("images")
        if images is None:
            raise ValueError("缺少输入图像")

        if not isinstance(images, list):
            images = [images]

        cols = context.params.get("cols", 3)
        rows = context.params.get("rows", 3)

        # 统一尺寸
        target_h = min(img.shape[0] for img in images)
        target_w = min(img.shape[1] for img in images)

        images_resized = []
        for img in images[:cols * rows]:
            img_resized = cv2.resize(img, (target_w, target_h))
            images_resized.append(img_resized)

        # 填充到指定数量
        while len(images_resized) < cols * rows:
            blank = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            images_resized.append(blank)

        # 组织成网格
        grid = []
        for r in range(rows):
            row_images = images_resized[r * cols:(r + 1) * cols]
            row = np.hstack(row_images)
            grid.append(row)

        result = np.vstack(grid)
        return {"image": result}

    def get_code_template(self, context: NodeContext) -> str:
        cols = context.params.get("cols", 3)
        rows = context.params.get("rows", 3)
        return f"""# 平铺图像
# 统一尺寸并组织成网格
target_h = min(img.shape[0] for img in images)
target_w = min(img.shape[1] for img in images)
images_resized = [cv2.resize(img, (target_w, target_h)) for img in images[:{cols * rows}]]
# 填充空白
while len(images_resized) < {cols * rows}:
    images_resized.append(np.zeros((target_h, target_w, 3), dtype=np.uint8))
# 组织网格
grid = [np.hstack(images_resized[r*{cols}:(r+1)*{cols}]) for r in range({rows})]
result = np.vstack(grid)
"""

