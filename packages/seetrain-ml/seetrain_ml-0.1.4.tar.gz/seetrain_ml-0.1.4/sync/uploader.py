#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 指标上传器模块

import sys
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from api import OpenAPI
from api.types import Metric as APIMetric
from log import seetrainlog
from data import Text
from .types import MetricType, MetricCategory
from .qm import Metric
from .circuit_breaker import CircuitBreaker
from .media_handler import MediaHandler


class MetricUploader:
    """指标上传器"""

    def __init__(self, api: Optional[OpenAPI] = None, task_id: Optional[str] = None):
        """
        初始化指标上传器
        
        Args:
            api: API客户端实例
            task_id: 任务ID
        """
        self.api = api or OpenAPI()
        self.task_id = task_id
        self._lock = threading.Lock()

        # 熔断器
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0
        )

        # 媒体处理器
        self.media_handler = MediaHandler(self.api, self.task_id)

        # 统计信息
        self._stats = {
            'total_uploaded': 0,
            'upload_errors': 0,
            'last_upload_time': None,
            'circuit_breaker_state': 'CLOSED'
        }

    def upload_metrics(self, metrics: List[Metric]) -> None:
        """
        上传指标
        
        Args:
            metrics: 指标列表
        """
        if not metrics:
            return

        # 分类指标
        metric_groups = self._classify_metrics(metrics)

        # 处理各类指标
        for metric_type, metric_list in metric_groups.items():
            if metric_list:
                self._upload_metrics_by_type(metric_type, metric_list)

    def _classify_metrics(self, metrics: List[Metric]) -> Dict[str, List[Metric]]:
        """分类指标"""
        text_metrics = []
        numeric_metrics = []
        media_metrics = []

        for metric in metrics:
            if self._is_media_type(metric):
                media_metrics.append(metric)
            elif self._is_text_type(metric):
                text_metrics.append(metric)
            else:
                numeric_metrics.append(metric)

        return {
            MetricCategory.TEXT: text_metrics,
            MetricCategory.NUMERIC: numeric_metrics,
            MetricCategory.MEDIA: media_metrics
        }

    def _upload_metrics_by_type(self, metric_type: str, metrics: List[Metric]) -> None:
        """根据类型上传指标"""
        if metric_type == MetricCategory.TEXT:
            self._upload_text_metrics(metrics)
        elif metric_type == MetricCategory.NUMERIC:
            self._upload_numeric_metrics(metrics)
        elif metric_type == MetricCategory.MEDIA:
            self._upload_media_metrics(metrics)

    def _upload_text_metrics(self, metrics: List[Metric]) -> None:
        """上传文本类型指标"""
        if not metrics:
            return

        try:
            api_metrics = self._create_api_metrics(metrics, MetricType.TEXT)
            self._upload_metrics_with_circuit_breaker(api_metrics)
        except Exception as e:
            error_msg = str(e)
            seetrainlog.error(f"上传文本指标失败: {error_msg}")
            raise e

    def _upload_numeric_metrics(self, metrics: List[Metric]) -> None:
        """上传数值类型指标"""
        if not metrics:
            return

        # 检查熔断器状态
        if not self.circuit_breaker.is_available():
            seetrainlog.warning("熔断器开启，跳过指标上传")
            raise Exception("Circuit breaker is OPEN")

        try:
            api_metrics = self._create_api_metrics(metrics, MetricType.NUMBER)
            self._upload_metrics_with_circuit_breaker(api_metrics)
        except Exception as e:
            error_msg = str(e)
            seetrainlog.error(f"上传数值指标失败: {error_msg}")
            raise e

    def _upload_media_metrics(self, metrics: List[Metric]) -> None:
        """上传媒体类型指标"""
        if not metrics:
            return

        try:
            api_metrics = self.media_handler.handle_media_metrics(metrics)
            if api_metrics:
                self._upload_metrics_with_circuit_breaker(api_metrics)
                seetrainlog.info(f"成功批量上传 {len(api_metrics)} 个媒体指标")
        except Exception as e:
            seetrainlog.error(f"批量上传媒体指标时发生错误: {e}")
            raise e

    def _create_api_metrics(self, metrics: List[Metric], mtype: str) -> List[Dict[str, Any]]:
        """创建API指标数据"""
        api_metrics = []
        for metric in metrics:
            metric_datetime = datetime.fromtimestamp(metric.timestamp)

            if mtype == MetricType.TEXT:
                api_metric = APIMetric(
                    task_id=self.task_id,
                    name=metric.name,
                    mtype=MetricType.TEXT,
                    step=metric.step,
                    text=metric.value.get_data(),
                    timestamp=metric_datetime
                )
            elif mtype == MetricType.NUMBER:
                api_metric = APIMetric(
                    task_id=self.task_id,
                    name=metric.name,
                    mtype=MetricType.NUMBER,
                    step=metric.step,
                    number=float(metric.value),
                    timestamp=metric_datetime
                )
            else:
                continue

            api_metrics.append(api_metric.model_dump(mode='json'))

        return api_metrics

    def _upload_metrics_with_circuit_breaker(self, api_metrics: List[Dict[str, Any]]) -> None:
        """通过熔断器上传指标"""
        try:
            self.circuit_breaker.call(
                self.api.batch_upload_metrics,
                api_metrics
            )

            # 更新统计
            with self._lock:
                self._stats['total_uploaded'] += len(api_metrics)
                self._stats['last_upload_time'] = datetime.now()
                self._stats['circuit_breaker_state'] = self.circuit_breaker.state

            seetrainlog.debug(f"成功上传 {len(api_metrics)} 个指标")

        except Exception as e:
            error_msg = str(e)
            seetrainlog.error(f"上传指标失败: {error_msg}")

            with self._lock:
                self._stats['upload_errors'] += 1
                self._stats['circuit_breaker_state'] = self.circuit_breaker.state

            raise e

    def _is_media_type(self, metric: Metric) -> bool:
        """判断是否为媒体类型指标"""
        # 根据指标名称或值类型判断
        media_keywords = ['image', 'audio', 'video']
        metric_name_lower = metric.name.lower()

        # 检查指标名称是否包含媒体关键词
        for keyword in media_keywords:
            if keyword in metric_name_lower:
                return True

        # 检查值类型
        if isinstance(metric.value, (str, dict, list)):
            return True

        return False

    def _is_text_type(self, metric: Metric) -> bool:
        """判断是否为文本类型指标"""
        return isinstance(metric.value, Text)

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'circuit_breaker_state': self.circuit_breaker.state,
                'circuit_breaker_failure_count': self.circuit_breaker.failure_count
            })
        return stats
