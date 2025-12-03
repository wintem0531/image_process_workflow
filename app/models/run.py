"""运行相关数据模型"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class RunStatus(str, Enum):
    """运行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(str, Enum):
    """节点状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class NodeOutput(BaseModel):
    """节点输出"""
    node_id: str = Field(..., description="节点ID")
    output_name: str = Field(..., description="输出端口名称")
    data_type: str = Field(..., description="数据类型: image, json, text")
    value: Optional[Any] = Field(None, description="输出值（Base64图像或JSON）")
    thumbnail: Optional[str] = Field(None, description="缩略图Base64")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class RunRequest(BaseModel):
    """运行请求"""
    workflow_id: str = Field(..., description="工作流ID")
    input_data: Optional[Dict[str, Any]] = Field(None, description="输入数据")
    node_id: Optional[str] = Field(None, description="从指定节点开始运行（单步调试）")
    max_concurrent: int = Field(4, description="最大并发数")


class RunResponse(BaseModel):
    """运行响应"""
    run_id: str = Field(..., description="运行ID")
    workflow_id: str = Field(..., description="工作流ID")
    status: RunStatus = Field(..., description="运行状态")
    created_at: str = Field(..., description="创建时间")
    started_at: Optional[str] = Field(None, description="开始时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
    error: Optional[str] = Field(None, description="错误信息")


class RunDetail(RunResponse):
    """运行详情"""
    node_statuses: Dict[str, NodeStatus] = Field(default_factory=dict, description="节点状态")
    node_outputs: Dict[str, List[NodeOutput]] = Field(default_factory=dict, description="节点输出")
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="运行日志")

