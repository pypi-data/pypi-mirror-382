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

__version__ = "0.1.2"
__author__ = "SeeTrain Team"
__email__ = "seetrain@example.com"
__description__ = "深度学习实验跟踪和框架集成工具"

# 导入核心功能
from .log import seetrainlog
from .setting import get_settings, set_settings, reset_settings

# 导入集成模块
from .integration import (
    init,
    log,
    log_scalar,
    log_image,
    log_audio,
    log_text,
    log_video,
    update_config,
    finish,
    with_integration
)

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
