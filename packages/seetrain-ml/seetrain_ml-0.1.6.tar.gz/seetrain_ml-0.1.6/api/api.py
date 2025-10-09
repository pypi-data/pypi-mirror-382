#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from .types import *
from toolkit import BuildRequest


class OpenAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.request = BuildRequest(headers={"Content-Type": "application/json"})

    def upsert_summary(self,
                       task_id: str,
                       project: str,
                       metrics: Dict[str, MetricsItem],
                       config: Optional[List[ConfigItem]] = None,
                       system: Optional[SystemInfo] = None,
                       python: Optional[PythonInfo] = None):
        summary = Summary(
            task_id=task_id,
            project=project,
            config=config,
            metrics=metrics,
            system=system,
            python=python)
        try:
            self.request.post(url=f"{self.base_url}/summary", body=summary.model_dump())
        except Exception as e:
            raise e

    def upload_metrics(self,
                       task_id: str,
                       name: str,
                       mtype: str,
                       value: Any):
        metric = Metric(
            task_id=task_id,
            name=name,
            mtype=mtype,
            value=value)
        try:
            self.request.post(url=f"{self.base_url}/metrics", body=metric.model_dump())
        except Exception as e:
            raise e

    def batch_upload_metrics(self, metrics: Any):
        try:
            self.request.post(url=f"{self.base_url}/metrics/batch", body=metrics)
        except Exception as e:
            raise e

    def batch_update_summary_metrics(self, task_id: str, metrics: Dict[str, Any]):
        """
        批量增量更新summary中的metrics
        
        Args:
            task_id: 任务ID
            metrics: 要更新的metrics字典
        """
        try:
            data = {
                "task_id": task_id,
                "metrics": metrics
            }
            return self.request.post(url=f"{self.base_url}/summary/metrics/batch", body=data)
        except Exception as e:
            raise e
        
    def upload_file_data(self, file_data: bytes, filename: str, file_type: str, task_id: str):
        """
        上传二进制文件数据到服务器

        Args:
            file_data: 文件的二进制数据
            filename: 文件名
            file_type: 文件类型 (如 'image/jpeg', 'text/plain' 等)
            task_id: 任务ID
        """
        try:
            return self.request.upload(
                url=f"{self.base_url}/file",
                filename=filename,
                file=file_data,
                file_type=file_type,
                task_id=task_id
            )
        except Exception as e:
            raise e
            
