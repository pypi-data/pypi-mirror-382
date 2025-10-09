#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
错误处理和容错机制模块

提供优雅降级、异常捕获、重试机制等错误处理功能
"""

import os
import sys
import time
import threading
import functools
from typing import Any, Dict, Optional, Union, List, Callable, Type, Tuple
from enum import Enum
from dataclasses import dataclass

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from log import seetrainlog


class ErrorLevel(Enum):
    """错误级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorInfo:
    """错误信息"""
    level: ErrorLevel
    message: str
    exception: Optional[Exception] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class IntegrationError(Exception):
    """集成错误基类"""
    
    def __init__(self, message: str, framework: str = None, context: Dict[str, Any] = None):
        super().__init__(message)
        self.framework = framework
        self.context = context or {}
        self.timestamp = time.time()


class FrameworkNotFoundError(IntegrationError):
    """框架未找到错误"""
    pass


class VersionIncompatibleError(IntegrationError):
    """版本不兼容错误"""
    pass


class ConfigurationError(IntegrationError):
    """配置错误"""
    pass


class DataConversionError(IntegrationError):
    """数据转换错误"""
    pass


class NetworkError(IntegrationError):
    """网络错误"""
    pass


class CircuitBreaker:
    """熔断器"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: Type[Exception] = Exception):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 失败阈值
            recovery_timeout: 恢复超时时间（秒）
            expected_exception: 预期的异常类型
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
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
        except self.expected_exception as e:
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


class RetryHandler:
    """重试处理器"""
    
    def __init__(self,
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        """
        初始化重试处理器
        
        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            exponential_base: 指数退避基数
            jitter: 是否添加随机抖动
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        重试执行函数
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 重试次数用尽后抛出最后一个异常
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    seetrainlog.error(f"Function {func.__name__} failed after {self.max_retries} retries: {e}")
                    raise e
                
                delay = self._calculate_delay(attempt)
                seetrainlog.warning(f"Function {func.__name__} failed (attempt {attempt + 1}/{self.max_retries + 1}), retrying in {delay:.2f}s: {e}")
                time.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # 添加±25%的抖动
        
        return delay


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self):
        self.error_history: List[ErrorInfo] = []
        self._lock = threading.Lock()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.retry_handlers: Dict[str, RetryHandler] = {}
    
    def handle_error(self, 
                     error: Exception,
                     level: ErrorLevel = ErrorLevel.ERROR,
                     context: Dict[str, Any] = None,
                     framework: str = None) -> None:
        """
        处理错误
        
        Args:
            error: 异常对象
            level: 错误级别
            context: 上下文信息
            framework: 框架名称
        """
        error_info = ErrorInfo(
            level=level,
            message=str(error),
            exception=error,
            context=context or {},
            timestamp=time.time()
        )
        
        with self._lock:
            self.error_history.append(error_info)
            # 保持最近1000个错误记录
            if len(self.error_history) > 1000:
                self.error_history = self.error_history[-1000:]
        
        # 根据错误级别记录日志
        if level == ErrorLevel.INFO:
            seetrainlog.info(f"Integration error: {error}")
        elif level == ErrorLevel.WARNING:
            seetrainlog.warning(f"Integration warning: {error}")
        elif level == ErrorLevel.ERROR:
            seetrainlog.error(f"Integration error: {error}")
        elif level == ErrorLevel.CRITICAL:
            seetrainlog.critical(f"Integration critical error: {error}")
    
    def get_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """获取熔断器"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(**kwargs)
        return self.circuit_breakers[name]
    
    def get_retry_handler(self, name: str, **kwargs) -> RetryHandler:
        """获取重试处理器"""
        if name not in self.retry_handlers:
            self.retry_handlers[name] = RetryHandler(**kwargs)
        return self.retry_handlers[name]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        with self._lock:
            if not self.error_history:
                return {}
            
            stats = {
                'total_errors': len(self.error_history),
                'error_levels': {},
                'recent_errors': [],
                'framework_errors': {}
            }
            
            # 统计错误级别
            for error_info in self.error_history:
                level = error_info.level.value
                stats['error_levels'][level] = stats['error_levels'].get(level, 0) + 1
                
                # 统计框架错误
                if error_info.context and 'framework' in error_info.context:
                    framework = error_info.context['framework']
                    stats['framework_errors'][framework] = stats['framework_errors'].get(framework, 0) + 1
            
            # 最近错误
            stats['recent_errors'] = [
                {
                    'level': error.level.value,
                    'message': error.message,
                    'timestamp': error.timestamp,
                    'framework': error.context.get('framework') if error.context else None
                }
                for error in self.error_history[-10:]  # 最近10个错误
            ]
            
            return stats


class GracefulDegradation:
    """优雅降级处理器"""
    
    def __init__(self, fallback_func: Optional[Callable] = None):
        """
        初始化优雅降级处理器
        
        Args:
            fallback_func: 降级函数
        """
        self.fallback_func = fallback_func
        self.error_handler = ErrorHandler()
    
    def with_fallback(self, fallback_func: Callable):
        """设置降级函数"""
        self.fallback_func = fallback_func
        return self
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数，失败时使用降级函数
        
        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果或降级函数结果
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.error_handler.handle_error(e, ErrorLevel.WARNING)
            
            if self.fallback_func:
                try:
                    seetrainlog.info(f"Using fallback function for {func.__name__}")
                    return self.fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    self.error_handler.handle_error(fallback_error, ErrorLevel.ERROR)
                    raise fallback_error
            else:
                raise e


def with_error_handling(level: ErrorLevel = ErrorLevel.ERROR,
                       context: Dict[str, Any] = None,
                       framework: str = None):
    """错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = ErrorHandler()
                error_handler.handle_error(e, level, context, framework)
                raise e
        return wrapper
    return decorator


def with_retry(max_retries: int = 3,
               base_delay: float = 1.0,
               max_delay: float = 60.0,
               exponential_base: float = 2.0,
               jitter: bool = True):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry_handler = RetryHandler(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter
            )
            return retry_handler.retry(func, *args, **kwargs)
        return wrapper
    return decorator


def with_circuit_breaker(failure_threshold: int = 5,
                        recovery_timeout: float = 60.0,
                        expected_exception: Type[Exception] = Exception):
    """熔断器装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            circuit_breaker = CircuitBreaker(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                expected_exception=expected_exception
            )
            return circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


def with_graceful_degradation(fallback_func: Optional[Callable] = None):
    """优雅降级装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            degradation = GracefulDegradation(fallback_func)
            return degradation.execute(func, *args, **kwargs)
        return wrapper
    return decorator


# 全局错误处理器实例
global_error_handler = ErrorHandler()


def handle_integration_error(error: Exception,
                           level: ErrorLevel = ErrorLevel.ERROR,
                           context: Dict[str, Any] = None,
                           framework: str = None) -> None:
    """处理集成错误"""
    global_error_handler.handle_error(error, level, context, framework)


def get_integration_error_stats() -> Dict[str, Any]:
    """获取集成错误统计"""
    return global_error_handler.get_error_stats()
