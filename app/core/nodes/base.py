"""节点基类"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel


class NodeContext(BaseModel):
    """节点执行上下文"""
    node_id: str
    inputs: Dict[str, Any]
    params: Dict[str, Any]
    input_data: Dict[str, Any]


class BaseNode(ABC):
    """节点基类"""

    @property
    @abstractmethod
    def node_type(self) -> str:
        """节点类型"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """节点名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """节点描述"""
        pass

    @property
    @abstractmethod
    def input_ports(self) -> Dict[str, str]:
        """输入端口定义 {port_name: description}"""
        pass

    @property
    @abstractmethod
    def output_ports(self) -> Dict[str, str]:
        """输出端口定义 {port_name: description}"""
        pass

    @property
    @abstractmethod
    def param_schema(self) -> Dict[str, Any]:
        """参数schema定义"""
        pass

    @abstractmethod
    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        """
        执行节点

        Args:
            context: 执行上下文

        Returns:
            输出字典 {output_port_name: output_value}
        """
        pass

    def get_code_template(self, context: NodeContext) -> str:
        """
        生成代码模板（用于导出）

        Args:
            context: 执行上下文

        Returns:
            Python 代码字符串
        """
        return f"# {self.name}\n# TODO: 实现代码生成"

