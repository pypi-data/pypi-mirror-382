#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SeeTrain 深度学习框架集成模块

本模块提供了多种适配模式来集成各种深度学习框架：
1. Callback模式 - 适用于PyTorch Lightning, Keras, Transformers等
2. Tracker模式 - 适用于Hugging Face Accelerate等
3. VisBackend模式 - 适用于MMEngine, MMDetection等
4. Autolog模式 - 适用于OpenAI, 智谱AI等API调用

核心设计理念：
- 统一的适配接口：通过seetrain.init()进行实验初始化
- 统一的日志接口：通过seetrain.log()记录各种类型的数据
- 统一的配置管理：通过seetrain.config管理超参数和配置
- 框架标识系统：每个集成都会在配置中标记使用的框架
"""

from .base import BaseIntegration
from .callback import CallbackIntegration
from .tracker import TrackerIntegration
from .visbackend import VisBackendIntegration
from .autolog import AutologIntegration

# 导入主要的API函数
from .main import (
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

__all__ = [
    'BaseIntegration',
    'CallbackIntegration', 
    'TrackerIntegration',
    'VisBackendIntegration',
    'AutologIntegration',
    # 主要API函数
    'init',
    'log',
    'log_scalar',
    'log_image',
    'log_audio',
    'log_text',
    'log_video',
    'update_config',
    'finish',
    'with_integration'
]
