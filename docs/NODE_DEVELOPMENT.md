# 节点开发文档

## 如何新增节点

### 1. 创建节点类

在 `app/core/nodes/` 目录下创建新的节点文件，继承 `BaseNode`：

```python
from app.core.nodes.base import BaseNode, NodeContext

class MyCustomNode(BaseNode):
    """自定义节点"""
    
    @property
    def node_type(self) -> str:
        return "MyCustomNode"
    
    @property
    def name(self) -> str:
        return "我的节点"
    
    @property
    def description(self) -> str:
        return "节点描述"
    
    @property
    def input_ports(self) -> Dict[str, str]:
        return {"image": "输入图像"}
    
    @property
    def output_ports(self) -> Dict[str, str]:
        return {"image": "输出图像"}
    
    @property
    def param_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "integer",
                    "description": "参数1",
                    "default": 10,
                },
            },
            "required": ["param1"],
        }
    
    async def execute(self, context: NodeContext) -> Dict[str, Any]:
        """执行节点逻辑"""
        image = context.inputs.get("image")
        param1 = context.params.get("param1", 10)
        
        # 处理逻辑
        result = process_image(image, param1)
        
        return {"image": result}
    
    def get_code_template(self, context: NodeContext) -> str:
        """生成代码模板"""
        param1 = context.params.get("param1", 10)
        return f"""# 自定义处理
result = process_image(image, {param1})
"""
```

### 2. 注册节点

在 `app/core/nodes/registry.py` 中导入并注册：

```python
from app.core.nodes.my_custom import MyCustomNode

class NodeRegistry:
    def register_all(self):
        nodes = [
            # ... 其他节点
            MyCustomNode(),
        ]
        for node in nodes:
            self.register(node.node_type, node)
```

### 3. 在前端分类中注册

在 `frontend/src/components/NodePalette.tsx` 中添加节点类型到相应分类：

```typescript
const nodeCategories: Record<string, string[]> = {
  '我的分类': ['MyCustomNode'],
  // ...
}
```

## 节点类型说明

### 输入节点
- 无输入端口
- 从文件或参数读取数据

### 处理节点
- 有输入和输出端口
- 执行图像处理操作

### 输出节点
- 有输入端口
- 用于显示或保存结果

## 参数 Schema

参数 schema 遵循 JSON Schema 格式：

```python
{
    "type": "object",
    "properties": {
        "param_name": {
            "type": "string" | "integer" | "number" | "boolean",
            "description": "参数描述",
            "default": "默认值",
            "enum": ["选项1", "选项2"],  # 可选：枚举值
        },
    },
    "required": ["param_name"],  # 必填参数列表
}
```

## 代码生成

`get_code_template` 方法应返回可执行的 Python 代码片段，该代码会：

1. 使用 `inputs` 字典访问输入数据
2. 使用 `params` 字典访问参数
3. 返回处理结果（通常赋值给 `result` 变量）

代码生成器会自动处理变量命名和依赖关系。

