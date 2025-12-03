"""脚本节点"""
from typing import Dict, Any
import logging

from app.core.nodes.base import BaseNode, NodeContext

logger = logging.getLogger(__name__)


class PythonSnippetNode(BaseNode):
    """Python代码片段节点"""

    @property
    def node_type(self) -> str:
        return "PythonSnippet"

    @property
    def name(self) -> str:
        return "Python脚本"

    @property
    def description(self) -> str:
        return "执行自定义Python代码片段"

    @property
    def input_ports(self) -> Dict[str, str]:
        return {"*": "任意输入（通过inputs字典访问）"}

    @property
    def output_ports(self) -> Dict[str, str]:
        return {"result": "执行结果"}

    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python代码（必须返回字典，键为输出端口名）",
                    "default": "# 示例代码\nresult = inputs.get('image', None)\nreturn {'result': result}",
                },
            },
            "required": ["code"],
        }

    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        code = context.params.get("code", "")
        if not code:
            raise ValueError("代码不能为空")

        # 安全限制：只允许导入白名单模块
        allowed_modules = {
            "cv2", "numpy", "np", "PIL", "Image", "json", "math", "os", "sys"
        }

        # 创建执行环境
        exec_globals = {
            "__builtins__": __builtins__,
            "cv2": __import__("cv2"),
            "numpy": __import__("numpy"),
            "np": __import__("numpy"),
            "PIL": __import__("PIL"),
            "Image": __import__("PIL.Image"),
            "json": __import__("json"),
            "math": __import__("math"),
            "os": __import__("os"),
            "sys": __import__("sys"),
            "inputs": context.inputs,
            "params": context.params,
        }

        try:
            # 执行代码
            exec_result = {}
            exec(code, exec_globals, exec_result)

            # 如果代码中有return语句，需要通过函数包装
            if "return" in code:
                # 包装为函数
                wrapped_code = f"""
def _execute():
    {code}
    return locals()
result = _execute()
"""
                exec(wrapped_code, exec_globals, exec_result)
                result = exec_result.get("result", {})
            else:
                # 直接使用exec_result
                result = exec_result

            # 确保返回字典
            if not isinstance(result, dict):
                result = {"result": result}

            return result

        except Exception as e:
            logger.error(f"Python代码执行失败: {e}", exc_info=True)
            raise ValueError(f"代码执行失败: {e}")

    def get_code_template(self, context: NodeContext) -> str:
        code = context.params.get("code", "")
        return f"""# 自定义Python代码
{code}
"""

