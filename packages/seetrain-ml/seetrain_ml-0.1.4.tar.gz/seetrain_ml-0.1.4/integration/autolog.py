#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Autolog模式集成

适用于OpenAI, 智谱AI等API调用
通过Monkey Patching动态替换API方法，拦截API调用并自动记录到SeeTrain
"""

import os
import sys
import asyncio
import functools
import inspect
import time
import threading
from typing import Any, Dict, Optional, Union, List, Callable, Sequence, TypeVar, Protocol
from abc import ABC, abstractmethod

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from .base import BaseIntegration
from .utils import get_module, register_integration
from log import seetrainlog

# 类型定义
K = TypeVar("K", bound=str)
V = TypeVar("V")


class Response(Protocol[K, V]):
    """响应协议"""
    def __getitem__(self, key: K) -> V: ...
    def get(self, key: K, default: Optional[V] = None) -> Optional[V]: ...


class ArgumentResponseResolver(Protocol):
    """参数响应解析器协议"""
    def __call__(self,
                 args: Sequence[Any],
                 kwargs: Dict[str, Any],
                 response: Response,
                 start_time: float,
                 time_elapsed: float,
                 lib_version: str = None) -> Optional[Dict[str, Any]]: ...


class AutologIntegration(BaseIntegration, ABC):
    """Autolog模式基础集成类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._patch_api = None
        self._original_methods: Dict[str, Any] = {}
        self._enabled = False
        self._lock = threading.Lock()
    
    @abstractmethod
    def _get_api_module_name(self) -> str:
        """获取API模块名称，子类必须实现"""
        pass
    
    @abstractmethod
    def _get_symbols(self) -> Sequence[str]:
        """获取要拦截的符号列表，子类必须实现"""
        pass
    
    @abstractmethod
    def _get_resolver(self) -> ArgumentResponseResolver:
        """获取响应解析器，子类必须实现"""
        pass
    
    def _initialize_framework(self) -> None:
        """初始化框架特定功能"""
        # 创建PatchAPI实例
        self._create_patch_api()
    
    def _create_patch_api(self) -> None:
        """创建PatchAPI实例"""
        api_module_name = self._get_api_module_name()
        symbols = self._get_symbols()
        resolver = self._get_resolver()
        
        self._patch_api = PatchAPI(
            name=self.framework_name,
            symbols=symbols,
            resolver=resolver,
            api_module_name=api_module_name,
            integration=self
        )
    
    def enable(self) -> None:
        """启用自动日志记录"""
        with self._lock:
            if self._enabled:
                seetrainlog.warning(f"{self.framework_name} autologging is already enabled")
                return
            
            if not self._initialized:
                self.init()
            
            seetrainlog.info(f"Enabling {self.framework_name} autologging")
            self._patch_api.patch()
            self._enabled = True
    
    def disable(self) -> None:
        """禁用自动日志记录"""
        with self._lock:
            if not self._enabled:
                return
            
            seetrainlog.info(f"Disabling {self.framework_name} autologging")
            self._patch_api.unpatch()
            self._enabled = False
    
    def __enter__(self):
        """上下文管理器入口"""
        self.enable()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disable()


class PatchAPI:
    """API拦截器"""
    
    def __init__(self, 
                 name: str, 
                 symbols: Sequence[str], 
                 resolver: ArgumentResponseResolver,
                 api_module_name: str,
                 integration: AutologIntegration):
        """
        初始化API拦截器
        
        Args:
            name: API名称
            symbols: 要拦截的符号列表
            resolver: 响应解析器
            api_module_name: API模块名称
            integration: 集成实例
        """
        self.name = name
        self.symbols = symbols
        self.resolver = resolver
        self.api_module_name = api_module_name
        self.integration = integration
        self.original_methods: Dict[str, Any] = {}
        self._api_module = None
    
    @property
    def api_module(self):
        """获取API模块"""
        if self._api_module is None:
            self._api_module = get_module(
                self.api_module_name,
                required=f"To use the SeeTrain {self.name} Autolog, "
                        f"you need to have the `{self.api_module_name}` python "
                        f"package installed. Please install it with `pip install {self.api_module_name}`.",
                lazy=False
            )
        return self._api_module
    
    def patch(self) -> None:
        """拦截API方法"""
        for symbol in self.symbols:
            try:
                # 分割符号，例如 "Client.generate" -> ["Client", "generate"]
                symbol_parts = symbol.split(".")
                
                # 获取原始方法
                original = functools.reduce(getattr, symbol_parts, self.api_module)
                
                def method_factory(original_method: Any, symbol_name: str):
                    """创建包装方法"""
                    
                    async def async_method(*args, **kwargs):
                        """异步方法包装器"""
                        start_time = time.perf_counter()
                        
                        try:
                            # 调用原始方法
                            result = await original_method(*args, **kwargs)
                            
                            # 计算耗时
                            end_time = time.perf_counter()
                            time_elapsed = end_time - start_time
                            
                            # 解析响应
                            loggable_dict = self.resolver(
                                args, kwargs, result, start_time, time_elapsed
                            )
                            
                            # 记录日志
                            if loggable_dict:
                                self.integration.log(loggable_dict)
                            
                            return result
                            
                        except Exception as e:
                            seetrainlog.error(f"Error in async method {symbol_name}: {e}")
                            raise
                    
                    def sync_method(*args, **kwargs):
                        """同步方法包装器"""
                        start_time = time.perf_counter()
                        
                        try:
                            # 调用原始方法
                            result = original_method(*args, **kwargs)
                            
                            # 计算耗时
                            end_time = time.perf_counter()
                            time_elapsed = end_time - start_time
                            
                            # 解析响应
                            loggable_dict = self.resolver(
                                args, kwargs, result, start_time, time_elapsed
                            )
                            
                            # 记录日志
                            if loggable_dict:
                                self.integration.log(loggable_dict)
                            
                            return result
                            
                        except Exception as e:
                            seetrainlog.error(f"Error in sync method {symbol_name}: {e}")
                            raise
                    
                    # 根据方法类型返回包装器
                    if inspect.iscoroutinefunction(original_method):
                        return functools.wraps(original_method)(async_method)
                    else:
                        return functools.wraps(original_method)(sync_method)
                
                # 保存原始方法
                self.original_methods[symbol] = original
                
                # 创建包装方法
                wrapped_method = method_factory(original, symbol)
                
                # 应用拦截
                if len(symbol_parts) == 1:
                    setattr(self.api_module, symbol_parts[0], wrapped_method)
                else:
                    setattr(
                        functools.reduce(getattr, symbol_parts[:-1], self.api_module),
                        symbol_parts[-1],
                        wrapped_method
                    )
                
                seetrainlog.debug(f"Patched method: {symbol}")
                
            except Exception as e:
                seetrainlog.error(f"Failed to patch method {symbol}: {e}")
    
    def unpatch(self) -> None:
        """恢复原始方法"""
        for symbol, original in self.original_methods.items():
            try:
                # 分割符号
                symbol_parts = symbol.split(".")
                
                # 恢复原始方法
                if len(symbol_parts) == 1:
                    setattr(self.api_module, symbol_parts[0], original)
                else:
                    setattr(
                        functools.reduce(getattr, symbol_parts[:-1], self.api_module),
                        symbol_parts[-1],
                        original
                    )
                
                seetrainlog.debug(f"Unpatched method: {symbol}")
                
            except Exception as e:
                seetrainlog.error(f"Failed to unpatch method {symbol}: {e}")
        
        # 清空原始方法记录
        self.original_methods.clear()


@register_integration('openai')
class OpenAIIntegration(AutologIntegration):
    """OpenAI集成"""
    
    def _get_framework_name(self) -> str:
        return "OpenAI"
    
    def _get_api_module_name(self) -> str:
        return "openai"
    
    def _get_symbols(self) -> Sequence[str]:
        """获取要拦截的符号"""
        try:
            import pkg_resources
            version = pkg_resources.get_distribution("openai").version
            
            # 根据版本选择不同的符号
            if version.startswith("0."):
                # 0.x版本
                return [
                    "ChatCompletion.create",
                    "Edit.create", 
                    "Completion.create",
                    "Edit.acreate",
                    "Completion.acreate",
                    "ChatCompletion.acreate"
                ]
            else:
                # 1.x版本
                return [
                    "chat.completions.create",
                    "completions.create"
                ]
        except Exception:
            # 默认使用1.x版本的符号
            return [
                "chat.completions.create",
                "completions.create"
            ]
    
    def _get_resolver(self) -> ArgumentResponseResolver:
        """获取响应解析器"""
        return OpenAIRequestResponseResolver()


class OpenAIRequestResponseResolver:
    """OpenAI请求响应解析器"""
    
    def __call__(self,
                 args: Sequence[Any],
                 kwargs: Dict[str, Any],
                 response: Response,
                 start_time: float,
                 time_elapsed: float,
                 lib_version: str = None) -> Optional[Dict[str, Any]]:
        """解析OpenAI请求和响应"""
        try:
            log_data = {}
            
            # 记录请求信息
            if kwargs:
                # 记录模型信息
                if 'model' in kwargs:
                    log_data['request/model'] = kwargs['model']
                
                # 记录消息数量
                if 'messages' in kwargs:
                    log_data['request/message_count'] = len(kwargs['messages'])
                
                # 记录参数
                for key in ['temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']:
                    if key in kwargs:
                        log_data[f'request/{key}'] = kwargs[key]
            
            # 记录响应信息
            if hasattr(response, 'usage'):
                usage = response.usage
                if hasattr(usage, 'prompt_tokens'):
                    log_data['response/prompt_tokens'] = usage.prompt_tokens
                if hasattr(usage, 'completion_tokens'):
                    log_data['response/completion_tokens'] = usage.completion_tokens
                if hasattr(usage, 'total_tokens'):
                    log_data['response/total_tokens'] = usage.total_tokens
            
            # 记录响应时间
            log_data['response/time_elapsed'] = time_elapsed
            
            # 记录选择数量
            if hasattr(response, 'choices'):
                log_data['response/choices_count'] = len(response.choices)
            
            return log_data if log_data else None
            
        except Exception as e:
            seetrainlog.error(f"Error parsing OpenAI response: {e}")
            return None


@register_integration('zhipuai')
class ZhipuAIIntegration(AutologIntegration):
    """智谱AI集成"""
    
    def _get_framework_name(self) -> str:
        return "ZhipuAI"
    
    def _get_api_module_name(self) -> str:
        return "zhipuai"
    
    def _get_symbols(self) -> Sequence[str]:
        """获取要拦截的符号"""
        return [
            "ChatCompletion.create",
            "ChatCompletion.acreate"
        ]
    
    def _get_resolver(self) -> ArgumentResponseResolver:
        """获取响应解析器"""
        return ZhipuAIRequestResponseResolver()


class ZhipuAIRequestResponseResolver:
    """智谱AI请求响应解析器"""
    
    def __call__(self,
                 args: Sequence[Any],
                 kwargs: Dict[str, Any],
                 response: Response,
                 start_time: float,
                 time_elapsed: float,
                 lib_version: str = None) -> Optional[Dict[str, Any]]:
        """解析智谱AI请求和响应"""
        try:
            log_data = {}
            
            # 记录请求信息
            if kwargs:
                # 记录模型信息
                if 'model' in kwargs:
                    log_data['request/model'] = kwargs['model']
                
                # 记录消息数量
                if 'messages' in kwargs:
                    log_data['request/message_count'] = len(kwargs['messages'])
                
                # 记录参数
                for key in ['temperature', 'max_tokens', 'top_p']:
                    if key in kwargs:
                        log_data[f'request/{key}'] = kwargs[key]
            
            # 记录响应信息
            if hasattr(response, 'usage'):
                usage = response.usage
                if hasattr(usage, 'prompt_tokens'):
                    log_data['response/prompt_tokens'] = usage.prompt_tokens
                if hasattr(usage, 'completion_tokens'):
                    log_data['response/completion_tokens'] = usage.completion_tokens
                if hasattr(usage, 'total_tokens'):
                    log_data['response/total_tokens'] = usage.total_tokens
            
            # 记录响应时间
            log_data['response/time_elapsed'] = time_elapsed
            
            # 记录选择数量
            if hasattr(response, 'choices'):
                log_data['response/choices_count'] = len(response.choices)
            
            return log_data if log_data else None
            
        except Exception as e:
            seetrainlog.error(f"Error parsing ZhipuAI response: {e}")
            return None


@register_integration('anthropic')
class AnthropicIntegration(AutologIntegration):
    """Anthropic集成"""
    
    def _get_framework_name(self) -> str:
        return "Anthropic"
    
    def _get_api_module_name(self) -> str:
        return "anthropic"
    
    def _get_symbols(self) -> Sequence[str]:
        """获取要拦截的符号"""
        return [
            "messages.create",
            "messages.acreate"
        ]
    
    def _get_resolver(self) -> ArgumentResponseResolver:
        """获取响应解析器"""
        return AnthropicRequestResponseResolver()


class AnthropicRequestResponseResolver:
    """Anthropic请求响应解析器"""
    
    def __call__(self,
                 args: Sequence[Any],
                 kwargs: Dict[str, Any],
                 response: Response,
                 start_time: float,
                 time_elapsed: float,
                 lib_version: str = None) -> Optional[Dict[str, Any]]:
        """解析Anthropic请求和响应"""
        try:
            log_data = {}
            
            # 记录请求信息
            if kwargs:
                # 记录模型信息
                if 'model' in kwargs:
                    log_data['request/model'] = kwargs['model']
                
                # 记录消息数量
                if 'messages' in kwargs:
                    log_data['request/message_count'] = len(kwargs['messages'])
                
                # 记录参数
                for key in ['temperature', 'max_tokens', 'top_p']:
                    if key in kwargs:
                        log_data[f'request/{key}'] = kwargs[key]
            
            # 记录响应信息
            if hasattr(response, 'usage'):
                usage = response.usage
                if hasattr(usage, 'input_tokens'):
                    log_data['response/input_tokens'] = usage.input_tokens
                if hasattr(usage, 'output_tokens'):
                    log_data['response/output_tokens'] = usage.output_tokens
                if hasattr(usage, 'total_tokens'):
                    log_data['response/total_tokens'] = usage.total_tokens
            
            # 记录响应时间
            log_data['response/time_elapsed'] = time_elapsed
            
            return log_data if log_data else None
            
        except Exception as e:
            seetrainlog.error(f"Error parsing Anthropic response: {e}")
            return None


# 便捷函数
def enable_openai_autolog(**kwargs):
    """启用OpenAI自动日志记录"""
    integration = OpenAIIntegration(**kwargs)
    integration.enable()
    return integration


def enable_zhipuai_autolog(**kwargs):
    """启用智谱AI自动日志记录"""
    integration = ZhipuAIIntegration(**kwargs)
    integration.enable()
    return integration


def enable_anthropic_autolog(**kwargs):
    """启用Anthropic自动日志记录"""
    integration = AnthropicIntegration(**kwargs)
    integration.enable()
    return integration
