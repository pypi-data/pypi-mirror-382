#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 指标同步功能 - 主入口和全局管理

import threading
import signal
import atexit
import sys
import os
from typing import Optional

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from api import OpenAPI
from env import Env

from .consumer import MetricConsumer
from log import seetrainlog

# 全局锁，保护全局变量访问
_global_lock = threading.Lock()

# 全局消费者实例
_global_consumer: Optional[MetricConsumer] = None


def get_consumer() -> MetricConsumer:
    """获取全局消费者实例"""
    global _global_consumer
    with _global_lock:
        if _global_consumer is None:
            _global_consumer = MetricConsumer()
        return _global_consumer


def start_consumer() -> None:
    """启动全局消费者"""
    consumer = get_consumer()
    consumer.start()
    # 自动设置优雅关闭处理器
    setup_graceful_shutdown()


def stop_consumer(wait_for_completion: bool = True, timeout: float = 60.0) -> None:
    """停止全局消费者
    
    Args:
        wait_for_completion: 是否等待指标消费完成
        timeout: 等待超时时间（秒）
    """
    global _global_consumer
    with _global_lock:
        if _global_consumer:
            _global_consumer.stop(wait_for_completion=wait_for_completion, timeout=timeout)
            _global_consumer = None


def _signal_handler(signum, frame):
    """信号处理器，用于优雅关闭"""
    seetrainlog.info(f"收到信号 {signum}，开始优雅关闭...")
    stop_consumer(wait_for_completion=True, timeout=30.0)
    sys.exit(0)


def _atexit_handler():
    """程序退出时的清理函数"""
    seetrainlog.info("程序退出，清理指标消费者...")
    stop_consumer(wait_for_completion=True, timeout=30.0)


def setup_graceful_shutdown():
    """设置优雅关闭处理器"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, _signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, _signal_handler)  # 终止信号

    # 注册退出处理器
    atexit.register(_atexit_handler)

    seetrainlog.info("已设置优雅关闭处理器")


# 向后兼容的API
def get_queue():
    """获取全局队列实例（向后兼容）"""
    consumer = get_consumer()
    return consumer.queue


def add_metric(name: str, value, step: Optional[int] = None, tags: Optional[dict] = None):
    """添加指标到队列（向后兼容）"""
    from .qm import Metric
    consumer = get_consumer()
    metric = Metric(
        name=name,
        value=value,
        timestamp=time.time(),
        step=step,
        tags=tags
    )
    return consumer.queue.add_metric(metric)


def get_stats():
    """获取统计信息（向后兼容）"""
    consumer = get_consumer()
    return consumer.get_stats()


def force_flush():
    """强制刷新队列（向后兼容）"""
    consumer = get_consumer()
    return consumer.force_flush()


# 导入时间模块用于向后兼容
import time