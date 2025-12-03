"""工作流路由"""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
import time

from app.models.workflow import Workflow, WorkflowCreate, WorkflowUpdate

router = APIRouter()

# 临时存储（生产环境应使用数据库）
workflows_db: dict[str, Workflow] = {}


@router.post("", response_model=Workflow)
async def create_workflow(workflow_data: WorkflowCreate):
    """创建工作流"""
    workflow_id = str(uuid.uuid4())
    workflow = Workflow(
        workflow_id=workflow_id,
        name=workflow_data.name or f"工作流 {workflow_id[:8]}",
        description=workflow_data.description,
        nodes=workflow_data.nodes,
        links=workflow_data.links,
        created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        updated_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    workflows_db[workflow_id] = workflow
    return workflow


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    """获取工作流"""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return workflows_db[workflow_id]


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, workflow_data: WorkflowUpdate):
    """更新工作流"""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="工作流不存在")

    workflow = workflows_db[workflow_id]
    if workflow_data.name is not None:
        workflow.name = workflow_data.name
    if workflow_data.description is not None:
        workflow.description = workflow_data.description
    if workflow_data.nodes is not None:
        workflow.nodes = workflow_data.nodes
    if workflow_data.links is not None:
        workflow.links = workflow_data.links
    workflow.updated_at = time.strftime("%Y-%m-%d %H:%M:%S")

    workflows_db[workflow_id] = workflow
    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """删除工作流"""
    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="工作流不存在")
    del workflows_db[workflow_id]
    return {"message": "工作流已删除"}


@router.get("", response_model=List[Workflow])
async def list_workflows():
    """列出所有工作流"""
    return list(workflows_db.values())

