#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 熔断器模式，防止连续失败

import threading
import time
from typing import Any, Callable


class CircuitBreaker:
    """熔断器模式，防止连续失败"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 失败阈值，连续失败次数超过此值将熔断
            recovery_timeout: 恢复超时时间（秒）
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        通过熔断器调用函数
        
        Args:
            func: 要调用的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 熔断器开启时抛出异常
        """
        with self._lock:
            if self.state == 'OPEN':
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """成功时的处理"""
        with self._lock:
            self.failure_count = 0
            self.state = 'CLOSED'
    
    def _on_failure(self):
        """失败时的处理"""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
    
    def is_available(self) -> bool:
        """检查熔断器是否可用"""
        with self._lock:
            if self.state == 'CLOSED':
                return True
            elif self.state == 'OPEN':
                return time.time() - self.last_failure_time > self.recovery_timeout
            else:  # HALF_OPEN
                return True
