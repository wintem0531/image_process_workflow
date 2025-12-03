# 快速开始指南

## 前置要求

- Python 3.12+
- Node.js 18+
- uv（Python 包管理器）
- Docker 和 Docker Compose（可选）

## 安装 uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 快速启动

### 方式一：使用启动脚本（推荐）

```bash
# 开发模式（启动后端和前端）
./start.sh dev
```

### 方式二：手动启动

#### 1. 启动后端

```bash
# 安装依赖
uv sync

# 启动服务
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 5050
```

后端将在 http://localhost:5050 启动

#### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

### 方式三：使用 Docker

```bash
docker-compose up
```

## 使用流程

1. **打开前端界面**: http://localhost:5173

2. **创建节点**: 从左侧节点面板拖拽节点到画布

3. **连接节点**: 从一个节点的输出端口拖拽到另一个节点的输入端口

4. **配置参数**: 选中节点，在右侧属性面板中配置参数

5. **运行工作流**: 点击"运行工作流"按钮

6. **查看结果**: 在运行面板中查看节点输出和预览图

7. **导出代码**: 点击"导出脚本"或"导出模块"按钮下载 Python 代码

## 示例工作流

### 示例1：图像灰度化和二值化

1. 添加 `ImageInput` 节点，设置图像路径
2. 添加 `Grayscale` 节点，连接到 ImageInput
3. 添加 `Threshold` 节点，连接到 Grayscale
4. 添加 `ImageViewer` 节点，连接到 Threshold
5. 运行工作流

### 示例2：查找轮廓并绘制矩形

1. 添加 `ImageInput` 节点
2. 添加 `Grayscale` 节点
3. 添加 `Threshold` 节点
4. 添加 `FindContours` 节点
5. 添加 `BoundingRect` 节点
6. 添加 `DrawRectangle` 节点，连接到原始图像和矩形数据
7. 运行工作流

## API 文档

启动后端后访问：http://localhost:5050/docs

## 常见问题

### Q: 前端无法连接到后端？

A: 检查后端是否在 5050 端口运行，前端代理配置是否正确。

### Q: 节点执行失败？

A: 检查节点参数是否正确，输入图像是否存在，查看运行面板的错误日志。

### Q: 如何添加自定义节点？

A: 参考 [节点开发文档](NODE_DEVELOPMENT.md)

