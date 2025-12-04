"""持久化存储服务"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.models.workflow import Workflow

logger = logging.getLogger(__name__)


class WorkflowStorage:
    """工作流持久化存储"""

    def __init__(self, storage_dir: str = "data/workflows"):
        """
        初始化存储服务

        Args:
            storage_dir: 存储目录路径
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._cache: Dict[str, Workflow] = {}
        self._load_index()

    def _load_index(self):
        """加载索引文件"""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    index = json.load(f)

                # 加载所有工作流到缓存
                for workflow_id in index.get("workflow_ids", []):
                    workflow = self._load_workflow_from_file(workflow_id)
                    if workflow:
                        self._cache[workflow_id] = workflow

                logger.info(f"从缓存加载了 {len(self._cache)} 个工作流")
            except Exception as e:
                logger.error(f"加载索引文件失败: {e}")
                self._cache = {}
        else:
            self._save_index()

    def _save_index(self):
        """保存索引文件"""
        try:
            index = {
                "workflow_ids": list(self._cache.keys()),
                "count": len(self._cache),
            }
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存索引文件失败: {e}")

    def _get_workflow_file(self, workflow_id: str) -> Path:
        """获取工作流文件路径"""
        return self.storage_dir / f"{workflow_id}.json"

    def _load_workflow_from_file(self, workflow_id: str) -> Optional[Workflow]:
        """从文件加载工作流"""
        file_path = self._get_workflow_file(workflow_id)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Workflow(**data)
        except Exception as e:
            logger.error(f"加载工作流文件失败 {workflow_id}: {e}")
            return None

    def _save_workflow_to_file(self, workflow: Workflow):
        """保存工作流到文件"""
        file_path = self._get_workflow_file(workflow.workflow_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(workflow.model_dump(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存工作流文件失败 {workflow.workflow_id}: {e}")
            raise

    def save(self, workflow: Workflow) -> Workflow:
        """
        保存工作流

        Args:
            workflow: 工作流对象

        Returns:
            保存后的工作流对象
        """
        self._cache[workflow.workflow_id] = workflow
        self._save_workflow_to_file(workflow)
        self._save_index()
        logger.info(f"工作流已保存: {workflow.workflow_id}")
        return workflow

    def get(self, workflow_id: str) -> Optional[Workflow]:
        """
        获取工作流

        Args:
            workflow_id: 工作流ID

        Returns:
            工作流对象，不存在则返回None
        """
        return self._cache.get(workflow_id)

    def delete(self, workflow_id: str) -> bool:
        """
        删除工作流

        Args:
            workflow_id: 工作流ID

        Returns:
            是否删除成功
        """
        if workflow_id not in self._cache:
            return False

        # 从缓存删除
        del self._cache[workflow_id]

        # 删除文件
        file_path = self._get_workflow_file(workflow_id)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"删除工作流文件失败 {workflow_id}: {e}")

        # 更新索引
        self._save_index()
        logger.info(f"工作流已删除: {workflow_id}")
        return True

    def list_all(self) -> List[Workflow]:
        """
        列出所有工作流

        Returns:
            工作流列表
        """
        return list(self._cache.values())

    def exists(self, workflow_id: str) -> bool:
        """
        检查工作流是否存在

        Args:
            workflow_id: 工作流ID

        Returns:
            是否存在
        """
        return workflow_id in self._cache

    def clear_all(self):
        """清空所有工作流（仅用于测试）"""
        for workflow_id in list(self._cache.keys()):
            self.delete(workflow_id)
