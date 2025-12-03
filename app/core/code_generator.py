"""代码生成器"""
from typing import Dict, List
from app.models.workflow import Workflow, Node, Link
from app.core.nodes.registry import NodeRegistry
from app.core.workflow import WorkflowEngine


class CodeGenerator:
    """代码生成器"""

    def __init__(self, node_registry: NodeRegistry):
        self.node_registry = node_registry
        self.engine = WorkflowEngine(node_registry)

    def generate_script(self, workflow: Workflow) -> str:
        """生成单文件脚本"""
        lines = [
            '"""',
            f"图像处理工作流脚本 - {workflow.name}",
            f"生成时间: {workflow.updated_at or workflow.created_at}",
            '"""',
            "",
            "import cv2",
            "import numpy as np",
            "from typing import Dict, Any, Optional",
            "",
            "",
            "def process_image(input_path: str, output_path: Optional[str] = None) -> np.ndarray:",
            '    """',
            "    处理图像",
            "",
            "    Args:",
            "        input_path: 输入图像路径",
            "        output_path: 输出图像路径（可选）",
            "",
            "    Returns:",
            "        处理后的图像",
            '    """',
            "    # 读取输入图像",
            "    image = cv2.imread(input_path)",
            "    if image is None:",
            '        raise ValueError(f"无法读取图像: {input_path}")',
            "",
        ]

        # 构建依赖图并拓扑排序
        graph = self.engine._build_graph(workflow)
        execution_order = self.engine._topological_sort(graph)
        node_map = {node.id: node for node in workflow.nodes}

        # 生成变量映射
        var_map: Dict[str, Dict[str, str]] = {}  # node_id -> {port: var_name}

        for node_id in execution_order:
            node = node_map[node_id]
            node_impl = self.node_registry.get(node.type)

            # 收集输入变量
            input_vars = {}
            for link in workflow.links:
                if link.to.node == node_id:
                    from_node_id = link.from_.node
                    from_port = link.from_.port
                    to_port = link.to.port

                    if from_node_id in var_map and from_port in var_map[from_node_id]:
                        input_vars[to_port] = var_map[from_node_id][from_port]

            # 生成节点代码
            context = type('NodeContext', (), {
                'node_id': node_id,
                'inputs': input_vars,
                'params': node.params,
                'input_data': {},
            })()

            code_template = node_impl.get_code_template(context)
            
            # 处理特殊输入（ImageInput）
            if node.type == "ImageInput":
                lines.append(f"    # {node_impl.name} (节点: {node_id})")
                code_lines = code_template.strip().split("\n")
                for line in code_lines:
                    lines.append("    " + line)
                # 输出变量
                output_var = f"image_{node_id}"
                var_map[node_id] = {"image": output_var}
                lines.append(f"    {output_var} = image")
            else:
                # 准备输入变量
                input_code = []
                for port, var_name in input_vars.items():
                    input_code.append(f"{port} = {var_name}")

                if input_code:
                    lines.append(f"    # {node_impl.name} (节点: {node_id})")
                    for line in input_code:
                        lines.append(f"    {line}")
                    code_lines = code_template.strip().split("\n")
                    for line in code_lines:
                        lines.append("    " + line)
                    
                    # 输出变量
                    output_ports = list(node_impl.output_ports.keys())
                    if len(output_ports) == 1:
                        output_var = f"result_{node_id}"
                        var_map[node_id] = {output_ports[0]: output_var}
                        lines.append(f"    {output_var} = result")
                    else:
                        for port in output_ports:
                            output_var = f"result_{node_id}_{port}"
                            if node_id not in var_map:
                                var_map[node_id] = {}
                            var_map[node_id][port] = output_var
                            lines.append(f"    {output_var} = result.get('{port}', None)")

        # 找到最终输出节点
        final_outputs = []
        for node_id in execution_order:
            node = node_map[node_id]
            if node.type == "ImageViewer" or not any(
                link.from_.node == node_id for link in workflow.links
            ):
                # 这是输出节点
                if node_id in var_map:
                    for port, var_name in var_map[node_id].items():
                        final_outputs.append(var_name)

        if final_outputs:
            lines.append("")
            lines.append("    # 返回最终结果")
            if len(final_outputs) == 1:
                lines.append(f"    return {final_outputs[0]}")
            else:
                lines.append("    return {")
                for var in final_outputs:
                    lines.append(f'        "{var}": {var},')
                lines.append("    }")
        else:
            lines.append("    return image")

        lines.extend([
            "",
            "",
            'if __name__ == "__main__":',
            '    import sys',
            '    if len(sys.argv) < 2:',
            '        print("用法: python script.py <input_image> [output_image]")',
            '        sys.exit(1)',
            '',
            '    input_path = sys.argv[1]',
            '    output_path = sys.argv[2] if len(sys.argv) > 2 else None',
            '',
            '    result = process_image(input_path, output_path)',
            '',
            '    if output_path:',
            '        cv2.imwrite(output_path, result)',
            '        print(f"结果已保存到: {output_path}")',
            '    else:',
            '        print("处理完成")',
        ])

        return "\n".join(lines)

    def generate_module(self, workflow: Workflow) -> str:
        """生成模块化代码"""
        # 简化实现：生成函数集合
        lines = [
            '"""',
            f"图像处理工作流模块 - {workflow.name}",
            f"生成时间: {workflow.updated_at or workflow.created_at}",
            '"""',
            "",
            "import cv2",
            "import numpy as np",
            "from typing import Dict, Any, Optional",
            "",
        ]

        # 为每个节点生成函数
        node_map = {node.id: node for node in workflow.nodes}
        for node_id, node in node_map.items():
            node_impl = self.node_registry.get(node.type)
            lines.append(f"def process_{node_id}(image: np.ndarray) -> np.ndarray:")
            lines.append(f'    """{node_impl.name}"""')
            context = type('NodeContext', (), {
                'node_id': node_id,
                'inputs': {},
                'params': node.params,
                'input_data': {},
            })()
            code = node_impl.get_code_template(context)
            lines.append("    " + code.replace("\n", "\n    ").strip())
            lines.append("    return result")
            lines.append("")

        # 生成主函数
        lines.append("def process_workflow(input_path: str) -> np.ndarray:")
        lines.append('    """执行完整工作流"""')
        lines.append("    image = cv2.imread(input_path)")
        lines.append("    if image is None:")
        lines.append('        raise ValueError(f"无法读取图像: {input_path}")')
        lines.append("")
        
        # 按拓扑顺序调用
        graph = self.engine._build_graph(workflow)
        execution_order = self.engine._topological_sort(graph)
        var_map = {}
        for node_id in execution_order:
            node = node_map[node_id]
            if node.type == "ImageInput":
                var_map[node_id] = "image"
            else:
                # 找到输入
                inputs = []
                for link in workflow.links:
                    if link.to.node == node_id:
                        from_node_id = link.from_.node
                        if from_node_id in var_map:
                            inputs.append(var_map[from_node_id])
                
                if inputs:
                    input_var = inputs[0] if len(inputs) == 1 else inputs[0]
                    lines.append(f"    # 处理节点 {node_id}")
                    lines.append(f"    {input_var} = process_{node_id}({input_var})")
                    var_map[node_id] = input_var

        lines.append("    return image")
        return "\n".join(lines)

