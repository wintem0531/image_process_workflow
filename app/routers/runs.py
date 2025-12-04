"""运行路由"""

import time
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.core.nodes.registry import NodeRegistry
from app.core.workflow import WorkflowEngine
from app.models.run import RunDetail, RunRequest, RunResponse
from app.routers.workflows import storage
from app.utils.image import image_to_base64, image_to_thumbnail

router = APIRouter()
node_registry = NodeRegistry()
node_registry.register_all()
workflow_engine = WorkflowEngine(node_registry)


@router.post("", response_model=RunResponse)
async def run_workflow(request: RunRequest, background_tasks: BackgroundTasks):
    """执行工作流"""
    workflow = storage.get(request.workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")

    run_id = str(uuid.uuid4())

    # 异步执行
    background_tasks.add_task(
        workflow_engine.execute,
        workflow,
        run_id,
        request.input_data,
        request.node_id,
        request.max_concurrent,
    )

    return RunResponse(
        run_id=run_id,
        workflow_id=request.workflow_id,
        status="running",
        created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    )


@router.get("/{run_id}", response_model=RunDetail)
async def get_run_status(run_id: str):
    """获取运行状态"""
    run_data = workflow_engine.get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="运行不存在")

    # 处理图像输出（转换为Base64）
    node_outputs = {}
    for node_id, outputs in run_data.get("node_outputs", {}).items():
        processed_outputs = []
        for output in outputs:
            # 如果是图像，转换为Base64
            if output.data_type == "image" and output.value is not None:
                import numpy as np

                if isinstance(output.value, np.ndarray):
                    output.thumbnail = image_to_thumbnail(output.value)
                    output.value = image_to_base64(output.value)
            processed_outputs.append(output)
        node_outputs[node_id] = processed_outputs

    return RunDetail(
        run_id=run_data["run_id"],
        workflow_id=run_data["workflow_id"],
        status=run_data["status"],
        created_at=run_data["created_at"],
        started_at=run_data.get("started_at"),
        completed_at=run_data.get("completed_at"),
        error=run_data.get("error"),
        node_statuses=run_data.get("node_statuses", {}),
        node_outputs=node_outputs,
        logs=run_data.get("logs", []),
    )


@router.get("/{run_id}/nodes/{node_id}/output")
async def get_node_output(run_id: str, node_id: str, output_name: Optional[str] = None):
    """获取节点输出"""
    run_data = workflow_engine.get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="运行不存在")

    node_outputs = run_data.get("node_outputs", {}).get(node_id, [])
    if not node_outputs:
        raise HTTPException(status_code=404, detail="节点输出不存在")

    if output_name:
        # 返回指定输出
        for output in node_outputs:
            if output.output_name == output_name:
                return output
        raise HTTPException(status_code=404, detail="输出端口不存在")
    else:
        # 返回所有输出
        return node_outputs


@router.post("/{run_id}/cancel")
async def cancel_run(run_id: str):
    """取消运行"""
    workflow_engine.cancel_run(run_id)
    return {"message": "运行已取消"}
