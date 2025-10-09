#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 指标消费者模块

import sys
import os
import threading
import time
import random
from typing import Dict, List, Optional, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..api import OpenAPI
from ..env import Env
from ..log import seetrainlog
from .qm import MetricsQueue, Metric
from .uploader import MetricUploader


class MetricConsumer:
    """指标队列消费者"""

    def __init__(self,
                 api: Optional[OpenAPI] = None,
                 batch_size: int = 50,
                 flush_interval: float = 5.0,
                 task_id: Optional[str] = None,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 circuit_breaker_threshold: int = 5):
        """
        初始化指标消费者
        
        Args:
            api: API客户端实例
            batch_size: 批量处理大小
            flush_interval: 刷新间隔（秒）
            task_id: 任务ID
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
            circuit_breaker_threshold: 熔断器失败阈值
        """
        self.api = api or OpenAPI(Env.BaseURL.value)
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.task_id = task_id or Env.TaskID.value
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        
        # 指标上传器
        self.uploader = MetricUploader(self.api, self.task_id)
        
        # 队列实例
        self.queue = MetricsQueue(maxsize=1000, batch_size=batch_size, timeout=flush_interval)

        # 统计信息
        self._stats = {
            'total_processed': 0,
            'total_uploaded': 0,
            'upload_errors': 0,
            'last_upload_time': None,
            'total_retried': 0,
            'total_failed': 0
        }

    def start(self) -> None:
        """启动消费者"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        seetrainlog.info("指标消费者已启动")

    def stop(self, wait_for_completion: bool = True, timeout: float = 30.0) -> None:
        """停止消费者
        
        Args:
            wait_for_completion: 是否等待指标消费完成
            timeout: 等待超时时间（秒）
        """
        if not self._running:
            return

        seetrainlog.info("正在停止指标消费者...")
        self._running = False

        if self._thread and self._thread.is_alive():
            if wait_for_completion:
                # 等待消费线程完成
                seetrainlog.info(f"等待指标消费完成，超时时间: {timeout}秒")
                self._thread.join(timeout=timeout)

                if self._thread.is_alive():
                    seetrainlog.warning(f"指标消费未在{timeout}秒内完成，强制停止")
                else:
                    seetrainlog.info("指标消费已完成")
            else:
                # 不等待，直接停止
                self._thread.join(timeout=1.0)

        # 停止前处理剩余的指标（确保所有指标都被处理完毕）
        seetrainlog.info("开始处理剩余指标...")
        self._flush_remaining_metrics()
        
        # 最终统计
        final_stats = self.get_stats()
        seetrainlog.info(f"指标消费者已停止，最终统计: {final_stats}")
        seetrainlog.info("指标消费者已停止")

    def _consume_loop(self) -> None:
        """消费循环"""
        while self._running:
            try:
                # 优先处理重试队列
                retry_metrics = self.queue.get_retry_metrics(
                    batch_size=self.batch_size,
                    timeout=0.1  # 短超时，优先处理重试
                )
                
                if retry_metrics:
                    seetrainlog.debug(f"处理 {len(retry_metrics)} 个重试指标")
                    self._process_metrics(retry_metrics)
                    continue
                
                # 处理正常队列
                metrics = self.queue.get_batch_metrics(
                    batch_size=self.batch_size,
                    timeout=self.flush_interval
                )

                if metrics:
                    self._process_metrics(metrics)
                else:
                    # 如果没有指标，等待一段时间
                    time.sleep(0.1)

            except Exception as e:
                seetrainlog.error(f"消费循环错误: {e}")
                time.sleep(1.0)

    def _process_metrics(self, metrics: List[Metric]) -> None:
        """处理指标数据"""
        if not metrics:
            return

        try:
            # 使用上传器处理指标
            self.uploader.upload_metrics(metrics)
            
            # 更新统计
            with self._lock:
                self._stats['total_processed'] += len(metrics)
                # 合并上传器统计
                uploader_stats = self.uploader.get_stats()
                self._stats['total_uploaded'] = uploader_stats['total_uploaded']
                self._stats['upload_errors'] = uploader_stats['upload_errors']
                self._stats['last_upload_time'] = uploader_stats['last_upload_time']
                
        except Exception as e:
            error_msg = str(e)
            seetrainlog.error(f"处理指标失败: {error_msg}")
            
            with self._lock:
                self._stats['upload_errors'] += 1
            
            # 处理失败的指标
            self._handle_failed_metrics(metrics, error_msg)

    def _handle_failed_metrics(self, metrics: List[Metric], error_msg: str) -> None:
        """处理失败的指标"""
        retry_metrics, failed_metrics = self._classify_failed_metrics(metrics, error_msg)
        
        # 处理重试指标
        if retry_metrics:
            self._add_metrics_to_retry_queue(retry_metrics)
        
        # 处理失败指标
        if failed_metrics:
            self._add_metrics_to_dead_letter_queue(failed_metrics)

    def _classify_failed_metrics(self, metrics: List[Metric], error_msg: str) -> tuple[List[Metric], List[Metric]]:
        """分类失败的指标为重试和失败"""
        retry_metrics = []
        failed_metrics = []
        
        for metric in metrics:
            metric.increment_retry(error_msg)
            
            if metric.can_retry():
                # 计算指数退避延迟
                delay = self.retry_delay * (2 ** metric.retry_count) + random.uniform(0, 1)
                metric.timestamp = time.time() + delay
                retry_metrics.append(metric)
            else:
                failed_metrics.append(metric)
        
        return retry_metrics, failed_metrics

    def _add_metrics_to_retry_queue(self, retry_metrics: List[Metric]) -> None:
        """将指标添加到重试队列"""
        for metric in retry_metrics:
            self.queue.add_to_retry_queue(metric)
        
        with self._lock:
            self._stats['total_retried'] += len(retry_metrics)
        seetrainlog.info(f"将 {len(retry_metrics)} 个指标加入重试队列")

    def _add_metrics_to_dead_letter_queue(self, failed_metrics: List[Metric]) -> None:
        """将指标添加到死信队列"""
        for metric in failed_metrics:
            self.queue.add_to_dead_letter_queue(metric)
        
        with self._lock:
            self._stats['total_failed'] += len(failed_metrics)
        seetrainlog.warning(f"将 {len(failed_metrics)} 个指标加入死信队列")

    def _flush_remaining_metrics(self) -> None:
        """刷新剩余指标，确保所有指标都被处理完毕"""
        seetrainlog.info("开始刷新剩余指标...")
        max_iterations = 100  # 防止无限循环
        
        try:
            for iteration in range(1, max_iterations + 1):
                processed_count = self._process_remaining_batch(iteration)
                
                if processed_count == 0:
                    seetrainlog.info(f"第{iteration}轮没有发现剩余指标，处理完成")
                    break
                
                time.sleep(0.1)  # 短暂等待，让异步操作完成
            
            self._log_final_queue_status(max_iterations)
                
        except Exception as e:
            seetrainlog.error(f"刷新剩余指标失败: {e}")
        
        # 等待所有异步操作完成
        self._wait_for_async_operations()

    def _process_remaining_batch(self, iteration: int) -> int:
        """处理一批剩余指标"""
        processed_count = 0
        
        # 处理主队列中的剩余指标
        remaining_metrics = self.queue.get_all_metrics()
        if remaining_metrics:
            seetrainlog.info(f"第{iteration}轮处理剩余 {len(remaining_metrics)} 个指标")
            self._process_metrics(remaining_metrics)
            processed_count += len(remaining_metrics)
        
        # 处理重试队列中的指标
        retry_metrics = self.queue.get_retry_metrics(batch_size=self.batch_size, timeout=0)
        if retry_metrics:
            seetrainlog.info(f"第{iteration}轮处理剩余 {len(retry_metrics)} 个重试指标")
            self._process_metrics(retry_metrics)
            processed_count += len(retry_metrics)
        
        return processed_count

    def _log_final_queue_status(self, max_iterations: int) -> None:
        """记录最终队列状态"""
        final_queue_size = self.queue.size()
        final_retry_size = len(self.queue.get_retry_metrics(batch_size=1, timeout=0))
        
        if final_queue_size > 0 or final_retry_size > 0:
            seetrainlog.warning(f"达到最大迭代次数({max_iterations})，仍有指标未处理: 主队列={final_queue_size}, 重试队列={final_retry_size}")
        else:
            seetrainlog.info("所有剩余指标已处理完毕")

    def _wait_for_async_operations(self) -> None:
        """等待所有异步操作完成"""
        seetrainlog.info("等待异步操作完成...")
        max_wait_time = 30  # 最大等待30秒
        wait_interval = 0.1  # 每100ms检查一次
        
        for total_waited in [i * wait_interval for i in range(int(max_wait_time / wait_interval))]:
            time.sleep(wait_interval)
            
            # 如果队列为空且没有其他异步操作，可以提前退出
            if self.queue.is_empty():
                time.sleep(0.5)  # 再等待一小段时间确保没有新的指标进入
                if self.queue.is_empty():
                    seetrainlog.info(f"异步操作完成，总等待时间: {total_waited:.1f}秒")
                    return
        
        seetrainlog.warning(f"异步操作等待超时({max_wait_time}秒)，强制继续")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            stats = self._stats.copy()
            stats.update({
                'queue_size': self.queue.size(),
                'queue_stats': self.queue.get_stats(),
                'is_running': self._running
            })
        return stats

    def force_flush(self) -> int:
        """强制刷新队列"""
        metrics = self.queue.get_batch_metrics(batch_size=self.batch_size, timeout=0)
        if metrics:
            self._process_metrics(metrics)
        return len(metrics)
    
    def get_dead_letter_metrics(self) -> List[Metric]:
        """获取死信队列中的指标"""
        return self.queue.get_dead_letter_metrics()
    
    def clear_dead_letter_queue(self) -> int:
        """清空死信队列"""
        return self.queue.clear_dead_letter_queue()
    
    def retry_dead_letter_metrics(self) -> int:
        """重试死信队列中的指标"""
        dead_letter_metrics = self.queue.get_dead_letter_metrics()
        if not dead_letter_metrics:
            return 0
        
        # 重置重试次数
        for metric in dead_letter_metrics:
            metric.retry_count = 0
            metric.last_error = None
            metric.timestamp = time.time()
        
        # 重新加入重试队列
        retry_count = 0
        for metric in dead_letter_metrics:
            if self.queue.add_to_retry_queue(metric):
                retry_count += 1
        
        seetrainlog.info(f"重新尝试 {retry_count} 个死信指标")
        return retry_count

    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()
