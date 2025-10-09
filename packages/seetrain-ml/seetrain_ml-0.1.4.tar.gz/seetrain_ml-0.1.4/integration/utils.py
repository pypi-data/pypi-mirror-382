#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
集成工具模块

提供动态模块加载、版本兼容性处理、数据类型转换等工具函数
"""

import importlib
import importlib.util
import os
import sys
import threading
import types
import packaging.version
from typing import Any, Dict, Optional, Union, List, Callable, TypeVar
from datetime import datetime

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from log import seetrainlog

# 全局不可导入模块集合
_not_importable = set()

T = TypeVar('T')


class LazyModuleState:
    """懒加载模块状态"""
    
    def __init__(self, module: types.ModuleType) -> None:
        self.module = module
        self.load_started = False
        self.lock = threading.RLock()
    
    def load(self) -> None:
        """加载模块"""
        with self.lock:
            if self.load_started:
                return
            self.load_started = True
            assert self.module.__spec__ is not None
            assert self.module.__spec__.loader is not None
            self.module.__spec__.loader.exec_module(self.module)
            self.module.__class__ = types.ModuleType


class LazyModule(types.ModuleType):
    """懒加载模块类"""
    
    def __getattribute__(self, name: str) -> Any:
        state = object.__getattribute__(self, "__lazy_module_state__")
        state.load()
        return object.__getattribute__(self, name)
    
    def __setattr__(self, name: str, value: Any) -> None:
        state = object.__getattribute__(self, "__lazy_module_state__")
        state.load()
        object.__setattr__(self, name, value)
    
    def __delattr__(self, name: str) -> None:
        state = object.__getattribute__(self, "__lazy_module_state__")
        state.load()
        object.__delattr__(self, name)


def import_module_lazy(name: str) -> types.ModuleType:
    """
    懒加载导入模块
    
    Args:
        name: 模块名称
        
    Returns:
        模块对象
    """
    try:
        return sys.modules[name]
    except KeyError:
        spec = importlib.util.find_spec(name)
        if spec is None:
            raise ModuleNotFoundError(f"Module {name} not found")
        module = importlib.util.module_from_spec(spec)
        module.__lazy_module_state__ = LazyModuleState(module)
        module.__class__ = LazyModule
        sys.modules[name] = module
        return module


def get_module(name: str, 
               required: Optional[Union[str, bool]] = None,
               lazy: bool = True) -> Any:
    """
    获取模块，支持懒加载
    
    Args:
        name: 模块名称
        required: 必需模块的错误信息
        lazy: 是否懒加载
        
    Returns:
        模块对象或None
    """
    if name not in _not_importable:
        try:
            if not lazy:
                return importlib.import_module(name)
            else:
                return import_module_lazy(name)
        except Exception as e:
            _not_importable.add(name)
            msg = f"Error importing optional module {name}: {e}"
            if required:
                seetrainlog.error(msg)
                raise ImportError(required) from e
            else:
                seetrainlog.warning(msg)
                return None
    return None


def get_optional_module(name: str) -> Optional[types.ModuleType]:
    """获取可选模块"""
    return get_module(name)


def check_version_compatibility(module_name: str, 
                               min_version: Optional[str] = None,
                               max_version: Optional[str] = None) -> bool:
    """
    检查模块版本兼容性
    
    Args:
        module_name: 模块名称
        min_version: 最小版本
        max_version: 最大版本
        
    Returns:
        是否兼容
    """
    try:
        module = get_module(module_name, lazy=False)
        if not hasattr(module, '__version__'):
            seetrainlog.warning(f"Module {module_name} has no version info")
            return True
        
        version = module.__version__
        
        if min_version and packaging.version.parse(version) < packaging.version.parse(min_version):
            seetrainlog.error(f"Module {module_name} version {version} is below minimum {min_version}")
            return False
        
        if max_version and packaging.version.parse(version) > packaging.version.parse(max_version):
            seetrainlog.warning(f"Module {module_name} version {version} is above maximum {max_version}")
            return False
        
        return True
        
    except Exception as e:
        seetrainlog.error(f"Error checking version compatibility for {module_name}: {e}")
        return False


def convert_tensor_to_numpy(tensor: Any) -> Any:
    """
    将张量转换为numpy数组
    
    Args:
        tensor: 张量对象
        
    Returns:
        numpy数组或原对象
    """
    try:
        # PyTorch tensor
        if hasattr(tensor, 'detach') and hasattr(tensor, 'cpu'):
            return tensor.detach().cpu().numpy()
        
        # TensorFlow tensor
        if hasattr(tensor, 'numpy'):
            return tensor.numpy()
        
        # JAX array
        if hasattr(tensor, 'to_py'):
            return tensor.to_py()
        
        # 其他情况返回原对象
        return tensor
        
    except Exception as e:
        seetrainlog.warning(f"Failed to convert tensor to numpy: {e}")
        return tensor


def flatten_dict(d: Dict[str, Any], 
                 parent_key: str = '', 
                 sep: str = '/') -> Dict[str, Any]:
    """
    扁平化嵌套字典
    
    Args:
        d: 嵌套字典
        parent_key: 父键名
        sep: 分隔符
        
    Returns:
        扁平化字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # 处理列表
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, v))
    return dict(items)


def sanitize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    清理配置，移除不可序列化的对象
    
    Args:
        config: 配置字典
        
    Returns:
        清理后的配置字典
    """
    sanitized = {}
    
    for key, value in config.items():
        try:
            # 检查是否可序列化
            import json
            json.dumps(value)
            sanitized[key] = value
        except (TypeError, ValueError):
            # 不可序列化，转换为字符串
            sanitized[key] = str(value)
            seetrainlog.debug(f"Converted non-serializable config {key} to string")
    
    return sanitized


def get_framework_info() -> Dict[str, Any]:
    """
    获取当前环境中的框架信息
    
    Returns:
        框架信息字典
    """
    frameworks = {}
    
    # 检查PyTorch
    torch = get_optional_module('torch')
    if torch:
        frameworks['pytorch'] = {
            'version': getattr(torch, '__version__', 'unknown'),
            'cuda_available': torch.cuda.is_available() if hasattr(torch, 'cuda') else False,
            'cuda_version': torch.version.cuda if hasattr(torch, 'version') else None
        }
    
    # 检查TensorFlow
    tf = get_optional_module('tensorflow')
    if tf:
        frameworks['tensorflow'] = {
            'version': getattr(tf, '__version__', 'unknown'),
            'gpu_available': len(tf.config.list_physical_devices('GPU')) > 0 if hasattr(tf, 'config') else False
        }
    
    # 检查JAX
    jax = get_optional_module('jax')
    if jax:
        frameworks['jax'] = {
            'version': getattr(jax, '__version__', 'unknown'),
            'devices': jax.devices() if hasattr(jax, 'devices') else []
        }
    
    # 检查PyTorch Lightning
    pl = get_optional_module('lightning')
    if pl:
        frameworks['pytorch_lightning'] = {
            'version': getattr(pl, '__version__', 'unknown')
        }
    
    # 检查Keras
    keras = get_optional_module('keras')
    if keras:
        frameworks['keras'] = {
            'version': getattr(keras, '__version__', 'unknown')
        }
    
    return frameworks


def create_metric_name(prefix: str, name: str, framework: str = '') -> str:
    """
    创建标准化的指标名称
    
    Args:
        prefix: 前缀
        name: 指标名称
        framework: 框架名称
        
    Returns:
        标准化指标名称
    """
    parts = []
    
    if framework:
        parts.append(framework.lower())
    
    if prefix:
        parts.append(prefix)
    
    parts.append(name)
    
    return '/'.join(parts)


def validate_metric_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    验证和清理指标数据
    
    Args:
        data: 指标数据
        
    Returns:
        验证后的数据
    """
    validated = {}
    
    for key, value in data.items():
        # 验证键名
        if not isinstance(key, str):
            seetrainlog.warning(f"Metric key must be string, got {type(key)}")
            continue
        
        # 清理键名
        clean_key = key.strip().replace(' ', '_')
        
        # 验证值
        if value is None:
            continue
        
        # 转换张量为numpy
        if hasattr(value, 'detach') or hasattr(value, 'numpy'):
            value = convert_tensor_to_numpy(value)
        
        validated[clean_key] = value
    
    return validated


class IntegrationRegistry:
    """集成注册表"""
    
    def __init__(self):
        self._integrations: Dict[str, type] = {}
        self._lock = threading.Lock()
    
    def register(self, name: str, integration_class: type) -> None:
        """注册集成类"""
        with self._lock:
            self._integrations[name] = integration_class
            seetrainlog.debug(f"Registered integration: {name}")
    
    def get(self, name: str) -> Optional[type]:
        """获取集成类"""
        with self._lock:
            return self._integrations.get(name)
    
    def list_all(self) -> List[str]:
        """列出所有注册的集成"""
        with self._lock:
            return list(self._integrations.keys())
    
    def create(self, name: str, **kwargs) -> Any:
        """创建集成实例"""
        integration_class = self.get(name)
        if not integration_class:
            raise ValueError(f"Integration {name} not found")
        
        return integration_class(**kwargs)


# 全局集成注册表
integration_registry = IntegrationRegistry()


def register_integration(name: str):
    """集成注册装饰器"""
    def decorator(cls):
        integration_registry.register(name, cls)
        return cls
    return decorator
