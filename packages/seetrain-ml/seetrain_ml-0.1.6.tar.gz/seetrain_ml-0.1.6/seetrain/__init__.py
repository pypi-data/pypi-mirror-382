#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SeeTrain - 深度学习实验跟踪和框架集成工具

SeeTrain 提供了多层次的适配架构，通过不同的集成模式来适配各种深度学习框架，
实现统一的实验跟踪体验。

主要特性:
- 多框架集成支持
- 统一的实验跟踪API
- 硬件监控功能
- 多媒体数据记录
- 丰富的可视化支持
"""

__version__ = "0.1.6"
__author__ = "SeeTrain Team"
__email__ = "seetrain@example.com"
__description__ = "深度学习实验跟踪和框架集成工具"

# 导入核心功能
from .log import seetrainlog
from .setting import get_settings, set_settings, reset_settings

# 导入数据模块(standalone API)
from .data import data as _data_module

# 导入集成模块(framework integration API)
from .integration import main as _integration_module

# 导入数据类型
from .data.modules import Image, Audio, Video, Text

# 导入框架特定集成
from .integration.main import (
    init_pytorch_lightning,
    init_keras,
    init_transformers,
    init_accelerate,
    init_mmengine,
    init_openai,
    enable_openai_autolog,
    enable_zhipuai_autolog,
    enable_anthropic_autolog
)


def init(framework=None, config=None, **kwargs):
    """
    初始化 SeeTrain
    
    支持两种使用模式:
    1. 简单模式 (standalone): seetrain.init(config={...})
    2. 框架集成模式: seetrain.init(framework='pytorch_lightning', **kwargs)
    
    Args:
        framework: 框架名称 (可选), 如 'pytorch_lightning', 'keras' 等
        config: 超参数配置字典 (可选), 用于简单模式
        **kwargs: 其他参数, 传递给框架集成
        
    Returns:
        框架集成模式返回集成实例, 简单模式返回 None
        
    Examples:
        # 简单模式
        import seetrain
        seetrain.init(config={"learning_rate": 0.01})
        
        # 框架集成模式
        import seetrain
        integration = seetrain.init(framework='pytorch_lightning')
    """
    # 如果指定了framework参数, 使用框架集成模式
    if framework is not None:
        return _integration_module.init(framework, **kwargs)
    
    # 否则使用简单的standalone模式
    return _data_module.init(config=config)


def log(data, value=None, step=None, epoch=None, print_to_console=True):
    """
    记录训练指标数据
    
    支持两种调用方式:
    1. 字典方式: log({"loss": 0.5, "acc": 0.95}, step=100)
    2. 键值对方式: log("loss", 0.5, step=100)
    
    Args:
        data: 指标数据字典 或 指标名称(字符串)
        value: 指标值 (仅在 data 是字符串时使用)
        step: 训练步数 (可选)
        epoch: 训练轮数 (可选)
        print_to_console: 是否打印到控制台
        
    Examples:
        # 字典方式
        seetrain.log({"loss": 0.5, "acc": 0.95}, step=100)
        seetrain.log({"image": Image("path/to/image.jpg")}, step=1)
        
        # 键值对方式
        seetrain.log("train/loss", 0.5, step=100)
        seetrain.log("train/acc", 0.95, step=100)
    """
    # 如果 data 是字符串, 转换为字典
    if isinstance(data, str):
        if value is None:
            raise ValueError("当使用键值对方式时, 必须提供 value 参数")
        data = {data: value}
    
    # 检查 data 是否是字典
    if not isinstance(data, dict):
        raise TypeError(f"data 参数必须是字典或字符串, 得到: {type(data)}")
    
    # 检查是否有活跃的框架集成
    active_integrations = _integration_module.list_integrations()
    
    if active_integrations:
        # 如果有活跃的框架集成, 使用集成模式
        _integration_module.log(data, step=step)
    else:
        # 否则使用简单模式
        _data_module.log(data, epoch=epoch, step=step, print_to_console=print_to_console)


def finish():
    """完成训练, 停止指标消费线程"""
    # 检查是否有活跃的框架集成
    active_integrations = _integration_module.list_integrations()
    
    if active_integrations:
        # 如果有活跃的框架集成, 使用集成模式
        _integration_module.finish()
    else:
        # 否则使用简单模式
        _data_module.finish()


# 导出其他集成模块函数
log_scalar = _integration_module.log_scalar
log_image = _integration_module.log_image
log_audio = _integration_module.log_audio
log_text = _integration_module.log_text
log_video = _integration_module.log_video
update_config = _integration_module.update_config
with_integration = _integration_module.with_integration

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    
    # 核心功能
    "seetrainlog",
    "get_settings",
    "set_settings", 
    "reset_settings",
    
    # 统一API
    "init",
    "log",
    "log_scalar",
    "log_image",
    "log_audio",
    "log_text",
    "log_video",
    "update_config",
    "finish",
    "with_integration",
    
    # 数据类型
    "Image",
    "Audio", 
    "Video",
    "Text",
    
    # 框架集成
    "init_pytorch_lightning",
    "init_keras",
    "init_transformers",
    "init_accelerate",
    "init_mmengine",
    "init_openai",
    "enable_openai_autolog",
    "enable_zhipuai_autolog",
    "enable_anthropic_autolog",
]
