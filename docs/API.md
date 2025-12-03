# API 文档

## 工作流 API

### 创建工作流
```http
POST /api/workflows
Content-Type: application/json

{
  "name": "工作流名称",
  "description": "工作流描述",
  "nodes": [...],
  "links": [...]
}
```

### 获取工作流
```http
GET /api/workflows/{workflow_id}
```

### 更新工作流
```http
PUT /api/workflows/{workflow_id}
Content-Type: application/json

{
  "name": "新名称",
  "nodes": [...],
  "links": [...]
}
```

### 删除工作流
```http
DELETE /api/workflows/{workflow_id}
```

### 列出所有工作流
```http
GET /api/workflows
```

## 节点 API

### 列出所有节点
```http
GET /api/nodes
```

### 获取节点信息
```http
GET /api/nodes/{node_type}
```

## 运行 API

### 执行工作流
```http
POST /api/runs
Content-Type: application/json

{
  "workflow_id": "workflow-id",
  "input_data": {},
  "node_id": "node-id",  // 可选：单步调试
  "max_concurrent": 4
}
```

### 获取运行状态
```http
GET /api/runs/{run_id}
```

### 获取节点输出
```http
GET /api/runs/{run_id}/nodes/{node_id}/output?output_name=image
```

### 取消运行
```http
POST /api/runs/{run_id}/cancel
```

## 导出 API

### 导出工作流代码
```http
POST /api/export/{workflow_id}?mode=script
```

模式：
- `script`: 单文件脚本
- `module`: 模块化代码

## 文件上传 API

### 上传文件
```http
POST /api/upload
Content-Type: multipart/form-data

file: <file>
```

