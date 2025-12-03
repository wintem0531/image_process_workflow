"""图像输入节点"""
import cv2
import numpy as np
from typing import Dict, Any
import base64
from io import BytesIO
from PIL import Image

from app.core.nodes.base import BaseNode, NodeContext


class ImageInputNode(BaseNode):
    """图像输入节点"""

    @property
    def node_type(self) -> str:
        return "ImageInput"

    @property
    def name(self) -> str:
        return "图像输入"

    @property
    def description(self) -> str:
        return "从文件路径或上传读取图像"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "图像文件路径",
                    "default": "",
                },
                "upload_id": {
                    "type": "string",
                    "description": "上传文件ID",
                    "default": "",
                },
            },
            "required": [],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        """执行节点"""
        path = context.params.get("path", "")
        upload_id = context.params.get("upload_id", "")

        if upload_id:
            # 从上传目录读取
            import os
            upload_path = os.path.join("uploads", upload_id)
            if os.path.exists(upload_path):
                path = upload_path

        if not path:
            raise ValueError("请提供图像路径或上传文件")

        # 读取图像
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"无法读取图像: {path}")

        return {"image": image}

    def get_code_template(self, context: NodeContext) -> str:
        path = context.params.get("path", "")
        upload_id = context.params.get("upload_id", "")
        
        if upload_id:
            return f"""# 读取图像
image = cv2.imread("uploads/{upload_id}")
if image is None:
    raise ValueError("无法读取图像")
"""
        else:
            return f"""# 读取图像
image = cv2.imread("{path}")
if image is None:
    raise ValueError("无法读取图像")
"""

