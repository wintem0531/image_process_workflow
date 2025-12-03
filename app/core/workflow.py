"""工作流执行引擎"""
import asyncio
import time
import uuid
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, deque
import logging

from app.models.workflow import Workflow, Node, Link, NodeStatus
from app.models.run import RunStatus, NodeOutput
from app.core.nodes.registry import NodeRegistry
from app.core.nodes.base import NodeContext

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """工作流执行引擎"""

    def __init__(self, node_registry: NodeRegistry):
        self.node_registry = node_registry
        self.runs: Dict[str, Dict[str, Any]] = {}  # run_id -> run_data

    async def execute(
        self,
        workflow: Workflow,
        run_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        start_node_id: Optional[str] = None,
        max_concurrent: int = 4,
    ) -> Dict[str, Any]:
        """
        执行工作流

        Args:
            workflow: 工作流定义
            run_id: 运行ID
            input_data: 输入数据
            start_node_id: 从指定节点开始运行（单步调试）
            max_concurrent: 最大并发数

        Returns:
            运行结果
        """
        input_data = input_data or {}
        start_time = time.time()

        # 初始化运行状态
        run_data = {
            "run_id": run_id,
            "workflow_id": workflow.workflow_id,
            "status": RunStatus.RUNNING,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "node_statuses": {},
            "node_outputs": {},
            "node_cache": {},  # 节点输出缓存
            "logs": [],
        }
        self.runs[run_id] = run_data

        try:
            # 构建依赖图
            graph = self._build_graph(workflow)
            
            # 拓扑排序
            if start_node_id:
                # 单步调试：只执行从指定节点开始的子图
                execution_order = self._get_subgraph_order(graph, start_node_id)
            else:
                # 完整执行
                execution_order = self._topological_sort(graph)

            # 执行节点
            await self._execute_nodes(
                workflow,
                execution_order,
                graph,
                run_data,
                input_data,
                max_concurrent,
            )

            run_data["status"] = RunStatus.COMPLETED
            run_data["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"Workflow {workflow.workflow_id} completed in {time.time() - start_time:.2f}s")

        except Exception as e:
            run_data["status"] = RunStatus.FAILED
            run_data["error"] = str(e)
            run_data["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.error(f"Workflow execution failed: {e}", exc_info=True)

        return run_data

    def _build_graph(self, workflow: Workflow) -> Dict[str, Dict[str, Any]]:
        """构建依赖图"""
        graph = {}
        
        # 初始化所有节点
        for node in workflow.nodes:
            graph[node.id] = {
                "node": node,
                "dependencies": [],  # 依赖的节点ID列表
                "dependents": [],  # 依赖此节点的节点ID列表
            }

        # 根据连接构建依赖关系
        for link in workflow.links:
            from_node_id = link.from_.node
            to_node_id = link.to.node
            
            if from_node_id in graph and to_node_id in graph:
                if from_node_id not in graph[to_node_id]["dependencies"]:
                    graph[to_node_id]["dependencies"].append(from_node_id)
                if to_node_id not in graph[from_node_id]["dependents"]:
                    graph[from_node_id]["dependents"].append(to_node_id)

        return graph

    def _topological_sort(self, graph: Dict[str, Dict[str, Any]]) -> List[str]:
        """拓扑排序"""
        in_degree = {node_id: len(info["dependencies"]) for node_id, info in graph.items()}
        queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            node_id = queue.popleft()
            result.append(node_id)

            for dependent_id in graph[node_id]["dependents"]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)

        if len(result) != len(graph):
            raise ValueError("工作流中存在循环依赖")

        return result

    def _get_subgraph_order(self, graph: Dict[str, Dict[str, Any]], start_node_id: str) -> List[str]:
        """获取从指定节点开始的子图执行顺序"""
        if start_node_id not in graph:
            raise ValueError(f"节点 {start_node_id} 不存在")

        # BFS 收集所有需要执行的节点
        visited = set()
        queue = deque([start_node_id])
        subgraph_nodes = set()

        while queue:
            node_id = queue.popleft()
            if node_id in visited:
                continue
            visited.add(node_id)
            subgraph_nodes.add(node_id)

            # 添加依赖节点
            for dep_id in graph[node_id]["dependencies"]:
                if dep_id not in visited:
                    queue.append(dep_id)

        # 对子图进行拓扑排序
        subgraph = {nid: graph[nid] for nid in subgraph_nodes}
        return self._topological_sort(subgraph)

    async def _execute_nodes(
        self,
        workflow: Workflow,
        execution_order: List[str],
        graph: Dict[str, Dict[str, Any]],
        run_data: Dict[str, Any],
        input_data: Dict[str, Any],
        max_concurrent: int,
    ):
        """执行节点（按拓扑顺序逐个执行）"""
        node_map = {node.id: node for node in workflow.nodes}

        # 构建端口映射：处理默认端口名称
        def get_input_port_name(node_type: str) -> str:
            """获取节点的默认输入端口名称"""
            node_impl = self.node_registry.get(node_type)
            input_ports = list(node_impl.input_ports.keys())
            return input_ports[0] if input_ports else "input"

        def get_output_port_name(node_type: str) -> str:
            """获取节点的默认输出端口名称"""
            node_impl = self.node_registry.get(node_type)
            output_ports = list(node_impl.output_ports.keys())
            return output_ports[0] if output_ports else "output"

        # 按拓扑顺序逐个执行
        for node_id in execution_order:
            node = node_map[node_id]
            run_data["node_statuses"][node_id] = NodeStatus.RUNNING
            
            try:
                # 收集输入数据
                inputs = {}
                for link in workflow.links:
                    if link.to.node == node_id:
                        from_node_id = link.from_.node
                        from_port = link.from_.port
                        to_port = link.to.port
                        
                        # 处理默认端口名称
                        if from_port in ("output", "default"):
                            from_node = node_map.get(from_node_id)
                            if from_node:
                                from_port = get_output_port_name(from_node.type)
                        
                        if to_port in ("input", "default"):
                            to_port = get_input_port_name(node.type)
                        
                        # 从缓存获取输入
                        if from_node_id in run_data["node_cache"]:
                            from_outputs = run_data["node_cache"][from_node_id]
                            if from_port in from_outputs:
                                inputs[to_port] = from_outputs[from_port]
                            else:
                                # 尝试获取第一个输出
                                if from_outputs:
                                    first_output = list(from_outputs.values())[0]
                                    inputs[to_port] = first_output

                logger.info(f"节点 {node_id} 输入: {list(inputs.keys())}")

                # 创建节点上下文
                context = NodeContext(
                    node_id=node_id,
                    inputs=inputs,
                    params=node.params,
                    input_data=input_data,
                )

                # 获取节点实现
                node_impl = self.node_registry.get(node.type)
                if not node_impl:
                    raise ValueError(f"未知节点类型: {node.type}")

                # 执行节点
                start_time = time.time()
                outputs = await node_impl.execute(context)
                duration = time.time() - start_time

                # 缓存输出
                run_data["node_cache"][node_id] = outputs
                
                # 记录输出
                node_outputs = []
                for output_name, output_value in outputs.items():
                    output = NodeOutput(
                        node_id=node_id,
                        output_name=output_name,
                        data_type=self._infer_data_type(output_value),
                        value=output_value,
                    )
                    node_outputs.append(output)
                run_data["node_outputs"][node_id] = node_outputs

                run_data["node_statuses"][node_id] = NodeStatus.SUCCESS
                run_data["logs"].append({
                    "node_id": node_id,
                    "type": "success",
                    "message": f"节点执行成功，耗时 {duration:.2f}s",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                })

            except Exception as e:
                run_data["node_statuses"][node_id] = NodeStatus.FAILED
                run_data["logs"].append({
                    "node_id": node_id,
                    "type": "error",
                    "message": str(e),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                })
                logger.error(f"节点 {node_id} 执行失败: {e}", exc_info=True)
                raise

    def _infer_data_type(self, value: Any) -> str:
        """推断数据类型"""
        import numpy as np
        if isinstance(value, np.ndarray) or (hasattr(value, "shape") and hasattr(value, "dtype")):
            return "image"
        elif isinstance(value, (dict, list)):
            return "json"
        else:
            return "text"

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """获取运行结果"""
        return self.runs.get(run_id)

    def cancel_run(self, run_id: str):
        """取消运行"""
        if run_id in self.runs:
            self.runs[run_id]["status"] = RunStatus.CANCELLED

