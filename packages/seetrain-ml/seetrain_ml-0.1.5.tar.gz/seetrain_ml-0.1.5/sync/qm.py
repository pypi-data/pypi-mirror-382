#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 指标同步队列

import queue
import threading
import time
from typing import Any, Dict, Optional, List, Union
from dataclasses import dataclass

# 导入项目中的数据类型
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data.modules import DataType


@dataclass
class Metric:
    """指标数据结构"""
    name: str
    value: DataType  # 使用项目定义的DataType
    timestamp: float
    step: Optional[int] = None  # 训练步数
    tags: Optional[Dict[str, str]] = None
    retry_count: int = 0  # 重试次数
    max_retries: int = 3  # 最大重试次数
    last_error: Optional[str] = None  # 最后一次错误信息

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}

    def can_retry(self) -> bool:
        """检查是否可以重试"""
        return self.retry_count < self.max_retries

    def increment_retry(self, error: Optional[str] = None) -> None:
        """增加重试次数"""
        self.retry_count += 1
        if error:
            self.last_error = error

    @classmethod
    def from_metrics_dict(cls, metrics_dict: Dict[str, DataType], step: Optional[int] = None) -> List['Metric']:
        """从指标字典创建Metric列表"""
        # 使用毫秒精度的时间戳
        current_time = time.time()
        return [
            cls(name=name, value=value, timestamp=current_time, step=step)
            for name, value in metrics_dict.items()
        ]


class MetricsQueue:
    """高性能线程安全的指标队列"""

    def __init__(self, maxsize: int = 0, batch_size: int = 100, timeout: float = 1.0):
        """
        初始化指标队列
        
        Args:
            maxsize: 队列最大大小，0表示无限制
            batch_size: 批量处理大小
            timeout: 批量获取超时时间（秒）
        """
        self._queue = queue.Queue(maxsize=maxsize)
        self._retry_queue = queue.Queue(maxsize=maxsize)  # 重试队列
        self._dead_letter_queue = queue.Queue(maxsize=maxsize)  # 死信队列
        self._lock = threading.RLock()  # 使用可重入锁
        self._batch_size = batch_size
        self._timeout = timeout
        self._stats = {
            'total_added': 0,
            'total_processed': 0,
            'total_dropped': 0,
            'queue_overflows': 0,
            'total_retried': 0,
            'total_failed': 0,
            'retry_queue_size': 0,
            'dead_letter_size': 0
        }

    def add_metric(self, name: str, value: DataType, step: Optional[int] = None,
                   tags: Optional[Dict[str, str]] = None) -> bool:
        """
        添加单个指标到队列
        
        Args:
            name: 指标名称
            value: 指标值 (DataType: int 或 float)
            step: 训练步数
            tags: 标签字典
            
        Returns:
            bool: 是否成功添加
        """
        return self.add_metrics([(name, value, step, tags)])

    def add_metrics_dict(self, metrics_dict: Dict[str, DataType], step: Optional[int] = None) -> int:
        """
        添加指标字典到队列（核心功能）
        
        Args:
            metrics_dict: 指标数据字典 {name: value}
            step: 训练步数
            
        Returns:
            int: 成功添加的指标数量
        """
        if not metrics_dict:
            return 0

        metrics = Metric.from_metrics_dict(metrics_dict, step)
        return self.add_metrics(metrics)

    def add_metrics(self, metrics_data: List[Union[tuple, Metric]]) -> int:
        """
        批量添加指标到队列
        
        Args:
            metrics_data: 指标数据列表，每个元素可以是 (name, value, step, tags) 元组或 Metric 对象
            
        Returns:
            int: 成功添加的指标数量
        """
        if not metrics_data:
            return 0

        success_count = 0
        # 使用毫秒精度的时间戳
        current_time = time.time()

        try:
            for item in metrics_data:
                if isinstance(item, Metric):
                    metric = item
                else:
                    # 处理元组格式 (name, value, step, tags)
                    if len(item) == 2:
                        name, value = item
                        step, tags = None, None
                    elif len(item) == 3:
                        name, value, step = item
                        tags = None
                    elif len(item) == 4:
                        name, value, step, tags = item
                    else:
                        continue

                    metric = Metric(
                        name=name,
                        value=value,
                        timestamp=current_time,
                        step=step,
                        tags=tags or {}
                    )

                try:
                    self._queue.put_nowait(metric)
                    success_count += 1
                    with self._lock:
                        self._stats['total_added'] += 1
                except queue.Full:
                    with self._lock:
                        self._stats['total_dropped'] += 1
                        self._stats['queue_overflows'] += 1
                    break

        except Exception as e:
            # 这里应该使用日志记录，但为了避免循环导入，暂时保持print
            print(f"Error adding metrics: {e}")

        return success_count

    def get_batch_metrics(self, batch_size: Optional[int] = None, timeout: Optional[float] = None) -> List[Metric]:
        """
        批量获取指标（核心功能）
        
        Args:
            batch_size: 批量大小，默认使用初始化时设置的值
            timeout: 超时时间（秒），默认使用初始化时设置的值
            
        Returns:
            List[Metric]: 指标列表
        """
        if batch_size is None:
            batch_size = self._batch_size
        if timeout is None:
            timeout = self._timeout

        metrics = []
        start_time = time.time()

        # 尝试获取第一个指标，如果队列为空则等待
        try:
            first_metric = self._queue.get(timeout=timeout)
            metrics.append(first_metric)
            with self._lock:
                self._stats['total_processed'] += 1
        except queue.Empty:
            return metrics

        # 批量获取剩余指标，不等待
        for _ in range(batch_size - 1):
            try:
                metric = self._queue.get_nowait()
                metrics.append(metric)
                with self._lock:
                    self._stats['total_processed'] += 1
            except queue.Empty:
                break

        return metrics

    def get_all_metrics(self) -> List[Metric]:
        """
        获取队列中的所有指标
        
        Returns:
            List[Metric]: 指标列表
        """
        metrics = []
        while True:
            try:
                metric = self._queue.get_nowait()
                metrics.append(metric)
                with self._lock:
                    self._stats['total_processed'] += 1
            except queue.Empty:
                break
        return metrics

    def size(self) -> int:
        """获取队列大小"""
        return self._queue.qsize()

    def is_empty(self) -> bool:
        """检查队列是否为空"""
        return self._queue.empty()

    def is_full(self) -> bool:
        """检查队列是否已满"""
        return self._queue.full()

    def clear(self) -> int:
        """
        清空队列
        
        Returns:
            int: 清空的指标数量
        """
        count = 0
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                count += 1
                with self._lock:
                    self._stats['total_processed'] += 1
            except queue.Empty:
                break
        return count

    def add_to_retry_queue(self, metric: Metric) -> bool:
        """
        将失败的指标添加到重试队列
        
        Args:
            metric: 失败的指标
            
        Returns:
            bool: 是否成功添加
        """
        try:
            self._retry_queue.put_nowait(metric)
            with self._lock:
                self._stats['total_retried'] += 1
                self._stats['retry_queue_size'] = self._retry_queue.qsize()
            return True
        except queue.Full:
            with self._lock:
                self._stats['total_dropped'] += 1
            return False

    def add_to_dead_letter_queue(self, metric: Metric) -> bool:
        """
        将最终失败的指标添加到死信队列
        
        Args:
            metric: 最终失败的指标
            
        Returns:
            bool: 是否成功添加
        """
        try:
            self._dead_letter_queue.put_nowait(metric)
            with self._lock:
                self._stats['total_failed'] += 1
                self._stats['dead_letter_size'] = self._dead_letter_queue.qsize()
            return True
        except queue.Full:
            with self._lock:
                self._stats['total_dropped'] += 1
            return False

    def get_retry_metrics(self, batch_size: Optional[int] = None, timeout: Optional[float] = None) -> List[Metric]:
        """
        从重试队列获取指标
        
        Args:
            batch_size: 批量大小
            timeout: 超时时间
            
        Returns:
            List[Metric]: 重试指标列表
        """
        if batch_size is None:
            batch_size = self._batch_size
        if timeout is None:
            timeout = self._timeout

        metrics = []
        start_time = time.time()

        # 尝试获取第一个指标
        try:
            first_metric = self._retry_queue.get(timeout=timeout)
            metrics.append(first_metric)
        except queue.Empty:
            return metrics

        # 批量获取剩余指标
        for _ in range(batch_size - 1):
            try:
                metric = self._retry_queue.get_nowait()
                metrics.append(metric)
            except queue.Empty:
                break

        # 更新统计
        with self._lock:
            self._stats['retry_queue_size'] = self._retry_queue.qsize()

        return metrics

    def get_dead_letter_metrics(self) -> List[Metric]:
        """
        获取死信队列中的所有指标
        
        Returns:
            List[Metric]: 死信指标列表
        """
        metrics = []
        while True:
            try:
                metric = self._dead_letter_queue.get_nowait()
                metrics.append(metric)
            except queue.Empty:
                break

        with self._lock:
            self._stats['dead_letter_size'] = self._dead_letter_queue.qsize()

        return metrics

    def clear_dead_letter_queue(self) -> int:
        """
        清空死信队列
        
        Returns:
            int: 清空的指标数量
        """
        count = 0
        while not self._dead_letter_queue.empty():
            try:
                self._dead_letter_queue.get_nowait()
                count += 1
            except queue.Empty:
                break

        with self._lock:
            self._stats['dead_letter_size'] = self._dead_letter_queue.qsize()

        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'current_size': self.size(),
                'is_empty': self.is_empty(),
                'is_full': self.is_full(),
                'batch_size': self._batch_size,
                'timeout': self._timeout,
                'retry_queue_size': self._retry_queue.qsize(),
                'dead_letter_size': self._dead_letter_queue.qsize()
            })
        return stats

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 退出时清空队列
        self.clear()
