"""数据节点"""
from typing import Dict, Any

from app.core.nodes.base import BaseNode, NodeContext


class JSONInputNode(BaseNode):
    """JSON输入节点"""

    @property
    def node_type(self) -> str:
        return "JSONInput"

    @property
    def name(self) -> str:
        return "JSON输入"

    @property
    def description(self) -> str:
        return "输入JSON数据（如矩形坐标等）"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"data": "输出JSON数据"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "json": {
                    "type": "string",
                    "description": "JSON字符串",
                    "default": "{}",
                },
            },
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        import json
        json_str = context.params.get("json", "{}")
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的JSON格式: {e}")

        return {"data": data}

    def get_code_template(self, context: NodeContext) -> str:
        json_str = context.params.get("json", "{}")
        return f"""# JSON输入
import json
data = json.loads('{json_str}')
"""


class JSONOutputNode(BaseNode):
    """JSON输出节点"""

    @property
    def node_type(self) -> str:
        return "JSONOutput"

    @property
    def name(self) -> str:
        return "JSON输出"

    @property
    def description(self) -> str:
        return "输出JSON数据"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"data": "输入数据"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"data": "输出JSON数据"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        data = context.inputs.get("data")
        if data is None:
            raise ValueError("缺少输入数据")

        return {"data": data}

    def get_code_template(self, context: NodeContext) -> str:
        return """# JSON输出
# 数据已通过输入传递
"""

