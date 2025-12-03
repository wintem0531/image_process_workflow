# 图像处理可视化工作流平台

一个可视化的图像处理工作流编辑与执行平台，支持节点化操作、可视化调试、代码导出等功能。

## 快速开始

### 一键启动（推荐）

```bash
# 开发模式
./start.sh dev

# 或使用 docker-compose
docker-compose up
```

### 手动启动

#### 后端

```bash
# 安装依赖
uv sync

# 启动服务
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 5050
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
.
├── app/                    # 后端应用
│   ├── main.py            # FastAPI 入口
│   ├── models/            # 数据模型
│   ├── routers/           # API 路由
│   ├── core/              # 核心引擎
│   │   ├── workflow.py    # 工作流引擎
│   │   └── nodes/         # 节点实现
│   └── utils/             # 工具函数
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── components/    # React 组件
│   │   ├── pages/         # 页面
│   │   └── utils/         # 工具函数
│   └── package.json
├── tests/                 # 测试
├── docker-compose.yml     # Docker 配置
└── start.sh              # 启动脚本
```

## API 文档

启动后端后访问：http://localhost:5050/docs

## 功能特性

- ✅ 节点化图像处理操作（25+ 内置节点）
- ✅ 可视化工作流编辑器（拖拽式界面）
- ✅ 实时预览和调试（单步执行、查看中间结果）
- ✅ Python 代码导出（脚本/模块两种模式）
- ✅ 批量处理支持
- ✅ RESTful API（自动生成 Swagger 文档）

## 内置节点

### 输入节点
- 图像输入（ImageInput）
- JSON输入（JSONInput）

### 基本处理
- 调整大小（Resize）
- 裁剪（Crop）
- 灰度化（Grayscale）
- 二值化（Threshold）
- 模糊（Blur）
- 高斯模糊（GaussianBlur）

### 形态学操作
- 腐蚀（Erode）
- 膨胀（Dilate）
- 开运算（Open）
- 闭运算（Close）

### 几何/轮廓
- 查找轮廓（FindContours）
- 外接矩形（BoundingRect）
- 最小外接矩形（MinAreaRect）

### 绘制
- 绘制矩形（DrawRectangle）
- 绘制文本（DrawText）
- 图层合成（Overlay）

### 拼接
- 水平拼接（ConcatHorizontal）
- 垂直拼接（ConcatVertical）
- 平铺（Tile）

### 查看器
- 图像查看器（ImageViewer）
- 差异查看器（DiffViewer）

### 脚本
- Python代码片段（PythonSnippet）

## 开发文档

- [API 文档](docs/API.md)
- [节点开发指南](docs/NODE_DEVELOPMENT.md)

## 测试

```bash
# 运行测试
uv run pytest

# 运行测试并显示覆盖率
uv run pytest --cov=app --cov-report=html
```

## 技术栈

- **后端**: FastAPI + Uvicorn + Python 3.12+
- **前端**: React + TypeScript + Vite + ReactFlow
- **图像处理**: OpenCV + NumPy + Pillow
- **依赖管理**: uv
- **容器化**: Docker + Docker Compose

## 许可证

MIT License

