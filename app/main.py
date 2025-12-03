"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.routers import workflows, nodes, runs, export, upload
from app.core.nodes.registry import NodeRegistry

app = FastAPI(
    title="图像处理工作流平台 API",
    description="可视化图像处理工作流编辑与执行平台",
    version="0.1.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（用于上传和输出）
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# 注册路由
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])
app.include_router(nodes.router, prefix="/api/nodes", tags=["nodes"])
app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])

# 初始化节点注册表
node_registry = NodeRegistry()
node_registry.register_all()


@app.get("/")
async def root():
    """根路径"""
    return {"message": "图像处理工作流平台 API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)

