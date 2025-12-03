"""代码导出路由"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.models.workflow import Workflow
from app.routers.workflows import workflows_db
from app.core.nodes.registry import NodeRegistry
from app.core.workflow import WorkflowEngine
from app.core.code_generator import CodeGenerator

router = APIRouter()
node_registry = NodeRegistry()
node_registry.register_all()


@router.post("/{workflow_id}")
async def export_workflow(workflow_id: str, mode: str = "script"):
    """
    导出工作流为Python代码

    Args:
        workflow_id: 工作流ID
        mode: 导出模式（script: 单文件脚本, module: 模块化代码）

    Returns:
        代码内容
    """
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = workflows_db[workflow_id]
    code_generator = CodeGenerator(node_registry)
    
    if mode == "script":
        code = code_generator.generate_script(workflow)
    elif mode == "module":
        code = code_generator.generate_module(workflow)
    else:
        raise HTTPException(status_code=400, detail="无效的导出模式")

    return {
        "workflow_id": workflow_id,
        "workflow_name": workflow.name,
        "mode": mode,
        "code": code,
    }

