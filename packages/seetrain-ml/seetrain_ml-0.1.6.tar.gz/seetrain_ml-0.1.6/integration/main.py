#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SeeTrain 深度学习框架集成主入口

提供统一的接口来初始化和使用各种深度学习框架的集成
"""

import os
import sys
from typing import Any, Dict, Optional, Union, List, Type
from enum import Enum

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from .base import BaseIntegration
from .callback import (
    PyTorchLightningIntegration,
    KerasIntegration,
    TransformersIntegration,
    UltralyticsIntegration
)
from .tracker import (
    AccelerateIntegration,
    RayTuneIntegration,
    OptunaIntegration,
    WandBIntegration
)
from .visbackend import (
    MMEngineIntegration,
    TensorBoardIntegration,
    MLflowIntegration
)
from .autolog import (
    OpenAIIntegration,
    ZhipuAIIntegration,
    AnthropicIntegration,
    enable_openai_autolog,
    enable_zhipuai_autolog,
    enable_anthropic_autolog
)
from .utils import integration_registry, get_framework_info
from .errors import handle_integration_error, ErrorLevel
from log import seetrainlog


class IntegrationMode(Enum):
    """集成模式"""
    CALLBACK = "callback"
    TRACKER = "tracker"
    VISBACKEND = "visbackend"
    AUTOLOG = "autolog"


class IntegrationManager:
    """集成管理器"""
    
    def __init__(self):
        self._active_integrations: Dict[str, BaseIntegration] = {}
        self._framework_info = get_framework_info()
    
    def init(self, 
             framework: str,
             mode: Optional[IntegrationMode] = None,
             **kwargs) -> BaseIntegration:
        """
        初始化框架集成
        
        Args:
            framework: 框架名称
            mode: 集成模式（可选，自动检测）
            **kwargs: 其他参数
            
        Returns:
            集成实例
        """
        try:
            # 自动检测模式
            if mode is None:
                mode = self._detect_mode(framework)
            
            # 获取集成类
            integration_class = self._get_integration_class(framework, mode)
            
            # 创建集成实例
            integration = integration_class(**kwargs)
            integration.init()
            
            # 注册活跃集成
            self._active_integrations[framework] = integration
            
            seetrainlog.info(f"Initialized {framework} integration with {mode.value} mode")
            return integration
            
        except Exception as e:
            handle_integration_error(e, ErrorLevel.ERROR, {'framework': framework, 'mode': mode})
            raise
    
    def _detect_mode(self, framework: str) -> IntegrationMode:
        """自动检测集成模式"""
        # 根据框架名称检测模式
        if framework.lower() in ['pytorch_lightning', 'keras', 'transformers', 'ultralytics']:
            return IntegrationMode.CALLBACK
        elif framework.lower() in ['accelerate', 'ray_tune', 'optuna', 'wandb']:
            return IntegrationMode.TRACKER
        elif framework.lower() in ['mmengine', 'tensorboard', 'mlflow']:
            return IntegrationMode.VISBACKEND
        elif framework.lower() in ['openai', 'zhipuai', 'anthropic']:
            return IntegrationMode.AUTOLOG
        else:
            # 默认使用callback模式
            return IntegrationMode.CALLBACK
    
    def _get_integration_class(self, framework: str, mode: IntegrationMode) -> Type[BaseIntegration]:
        """获取集成类"""
        # 直接映射
        integration_map = {
            # Callback模式
            'pytorch_lightning': PyTorchLightningIntegration,
            'keras': KerasIntegration,
            'transformers': TransformersIntegration,
            'ultralytics': UltralyticsIntegration,
            
            # Tracker模式
            'accelerate': AccelerateIntegration,
            'ray_tune': RayTuneIntegration,
            'optuna': OptunaIntegration,
            'wandb': WandBIntegration,
            
            # VisBackend模式
            'mmengine': MMEngineIntegration,
            'tensorboard': TensorBoardIntegration,
            'mlflow': MLflowIntegration,
            
            # Autolog模式
            'openai': OpenAIIntegration,
            'zhipuai': ZhipuAIIntegration,
            'anthropic': AnthropicIntegration,
        }
        
        framework_lower = framework.lower()
        if framework_lower in integration_map:
            return integration_map[framework_lower]
        
        # 尝试从注册表获取
        integration_class = integration_registry.get(framework_lower)
        if integration_class:
            return integration_class
        
        raise ValueError(f"Unsupported framework: {framework}")
    
    def get_integration(self, framework: str) -> Optional[BaseIntegration]:
        """获取活跃的集成实例"""
        return self._active_integrations.get(framework)
    
    def list_active_integrations(self) -> List[str]:
        """列出所有活跃的集成"""
        return list(self._active_integrations.keys())
    
    def finish_all(self) -> None:
        """完成所有集成"""
        for framework, integration in self._active_integrations.items():
            try:
                integration.finish()
                seetrainlog.info(f"Finished {framework} integration")
            except Exception as e:
                handle_integration_error(e, ErrorLevel.WARNING, {'framework': framework})
        
        self._active_integrations.clear()
    
    def get_framework_info(self) -> Dict[str, Any]:
        """获取框架信息"""
        return self._framework_info.copy()


# 全局集成管理器实例
_integration_manager = IntegrationManager()


def init(framework: str, **kwargs) -> BaseIntegration:
    """
    初始化框架集成
    
    Args:
        framework: 框架名称
        **kwargs: 其他参数
        
    Returns:
        集成实例
    """
    return _integration_manager.init(framework, **kwargs)


def log(data: Dict[str, Any], step: Optional[int] = None) -> None:
    """
    记录数据到所有活跃的集成
    
    Args:
        data: 要记录的数据
        step: 步骤数
    """
    for integration in _integration_manager._active_integrations.values():
        try:
            integration.log(data, step=step)
        except Exception as e:
            handle_integration_error(e, ErrorLevel.WARNING)


def log_scalar(name: str, value: Union[int, float], step: Optional[int] = None) -> None:
    """记录标量值"""
    log({name: value}, step=step)


def log_image(name: str, image: Any, step: Optional[int] = None, **kwargs) -> None:
    """记录图像"""
    for integration in _integration_manager._active_integrations.values():
        try:
            integration.log_image(name, image, step=step, **kwargs)
        except Exception as e:
            handle_integration_error(e, ErrorLevel.WARNING)


def log_audio(name: str, audio: Any, step: Optional[int] = None, **kwargs) -> None:
    """记录音频"""
    for integration in _integration_manager._active_integrations.values():
        try:
            integration.log_audio(name, audio, step=step, **kwargs)
        except Exception as e:
            handle_integration_error(e, ErrorLevel.WARNING)


def log_text(name: str, text: str, step: Optional[int] = None) -> None:
    """记录文本"""
    log({name: text}, step=step)


def update_config(config: Dict[str, Any]) -> None:
    """更新配置"""
    for integration in _integration_manager._active_integrations.values():
        try:
            integration.update_config(config)
        except Exception as e:
            handle_integration_error(e, ErrorLevel.WARNING)


def finish() -> None:
    """完成所有集成"""
    _integration_manager.finish_all()


def get_integration(framework: str) -> Optional[BaseIntegration]:
    """获取集成实例"""
    return _integration_manager.get_integration(framework)


def list_integrations() -> List[str]:
    """列出所有活跃的集成"""
    return _integration_manager.list_active_integrations()


def get_framework_info() -> Dict[str, Any]:
    """获取框架信息"""
    return _integration_manager.get_framework_info()


# 便捷函数
def init_pytorch_lightning(**kwargs) -> PyTorchLightningIntegration:
    """初始化PyTorch Lightning集成"""
    return init('pytorch_lightning', **kwargs)


def init_keras(**kwargs) -> KerasIntegration:
    """初始化Keras集成"""
    return init('keras', **kwargs)


def init_transformers(**kwargs) -> TransformersIntegration:
    """初始化Transformers集成"""
    return init('transformers', **kwargs)


def init_accelerate(**kwargs) -> AccelerateIntegration:
    """初始化Accelerate集成"""
    return init('accelerate', **kwargs)


def init_mmengine(**kwargs) -> MMEngineIntegration:
    """初始化MMEngine集成"""
    return init('mmengine', **kwargs)


def init_openai(**kwargs) -> OpenAIIntegration:
    """初始化OpenAI集成"""
    return init('openai', **kwargs)


# 自动日志记录便捷函数
def enable_openai_autolog(**kwargs):
    """启用OpenAI自动日志记录"""
    return enable_openai_autolog(**kwargs)


def enable_zhipuai_autolog(**kwargs):
    """启用智谱AI自动日志记录"""
    return enable_zhipuai_autolog(**kwargs)


def enable_anthropic_autolog(**kwargs):
    """启用Anthropic自动日志记录"""
    return enable_anthropic_autolog(**kwargs)


# 上下文管理器支持
class IntegrationContext:
    """集成上下文管理器"""
    
    def __init__(self, framework: str, **kwargs):
        self.framework = framework
        self.kwargs = kwargs
        self.integration = None
    
    def __enter__(self):
        self.integration = init(self.framework, **self.kwargs)
        return self.integration
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.integration:
            self.integration.finish()


def with_integration(framework: str, **kwargs):
    """集成上下文管理器装饰器"""
    return IntegrationContext(framework, **kwargs)


# 导出主要接口
__all__ = [
    'init',
    'log',
    'log_scalar',
    'log_image',
    'log_audio',
    'log_text',
    'update_config',
    'finish',
    'get_integration',
    'list_integrations',
    'get_framework_info',
    'init_pytorch_lightning',
    'init_keras',
    'init_transformers',
    'init_accelerate',
    'init_mmengine',
    'init_openai',
    'enable_openai_autolog',
    'enable_zhipuai_autolog',
    'enable_anthropic_autolog',
    'with_integration',
    'IntegrationMode',
    'IntegrationManager'
]
