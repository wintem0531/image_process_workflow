"""节点路由"""
from fastapi import APIRouter
from typing import List

from app.core.nodes.registry import NodeRegistry

router = APIRouter()
node_registry = NodeRegistry()
node_registry.register_all()


@router.get("")
async def list_nodes():
    """列出所有可用节点"""
    return node_registry.list_all()


@router.get("/{node_type}")
async def get_node_info(node_type: str):
    """获取节点信息"""
    try:
        node = node_registry.get(node_type)
        return {
            "type": node_type,
            "name": node.name,
            "description": node.description,
            "input_ports": node.input_ports,
            "output_ports": node.output_ports,
            "param_schema": node.param_schema,
        }
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))

