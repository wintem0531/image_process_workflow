"""工作流数据模型"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class NodePort(BaseModel):
    """节点端口"""
    node: str = Field(..., description="节点ID")
    port: str = Field(..., description="端口名称")


class Link(BaseModel):
    """连接"""
    from_: NodePort = Field(..., alias="from", description="源端口")
    to: NodePort = Field(..., description="目标端口")

    class Config:
        populate_by_name = True


class NodeStatus(str, Enum):
    """节点运行状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class Node(BaseModel):
    """节点"""
    id: str = Field(..., description="节点唯一ID")
    type: str = Field(..., description="节点类型")
    params: Dict[str, Any] = Field(default_factory=dict, description="节点参数")
    inputs: List[NodePort] = Field(default_factory=list, description="输入连接")
    outputs: List[str] = Field(default_factory=list, description="输出端口名称列表")
    position: Optional[Dict[str, float]] = Field(None, description="节点在画布上的位置")
    status: Optional[NodeStatus] = Field(None, description="运行状态")
    preview: Optional[str] = Field(None, description="预览图Base64")


class Workflow(BaseModel):
    """工作流"""
    workflow_id: str = Field(..., description="工作流ID")
    name: Optional[str] = Field(None, description="工作流名称")
    description: Optional[str] = Field(None, description="工作流描述")
    nodes: List[Node] = Field(default_factory=list, description="节点列表")
    links: List[Link] = Field(default_factory=list, description="连接列表")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")


class WorkflowCreate(BaseModel):
    """创建工作流请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: List[Node] = Field(default_factory=list)
    links: List[Link] = Field(default_factory=list)


class WorkflowUpdate(BaseModel):
    """更新工作流请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[Node]] = None
    links: Optional[List[Link]] = None

