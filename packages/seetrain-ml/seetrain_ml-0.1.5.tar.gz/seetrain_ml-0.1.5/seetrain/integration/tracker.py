#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tracker模式集成

适用于Hugging Face Accelerate等框架
通过实现框架的Tracker接口，将框架的日志调用直接转发给SeeTrain
"""

import os
import sys
from typing import Any, Dict, Optional, Union, List
from abc import ABC, abstractmethod

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from .base import BaseIntegration
from .utils import get_module, register_integration
from ..log import seetrainlog


class TrackerIntegration(BaseIntegration, ABC):
    """Tracker模式基础集成类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._tracker_instance = None
        self._framework_module = None
    
    @abstractmethod
    def _get_tracker_class(self):
        """获取框架的Tracker基类，子类必须实现"""
        pass
    
    @abstractmethod
    def _get_framework_module_name(self) -> str:
        """获取框架模块名称，子类必须实现"""
        pass
    
    def _initialize_framework(self) -> None:
        """初始化框架特定功能"""
        # 获取框架模块
        module_name = self._get_framework_module_name()
        self._framework_module = get_module(module_name, required=f"Framework {module_name} not found")
        
        if not self._framework_module:
            raise ImportError(f"Failed to import {module_name}")
        
        # 创建Tracker实例
        self._create_tracker_instance()
    
    def _create_tracker_instance(self) -> None:
        """创建Tracker实例"""
        tracker_class = self._get_tracker_class()
        self._tracker_instance = tracker_class()
        seetrainlog.debug(f"Created tracker instance: {tracker_class.__name__}")
    
    def get_tracker(self):
        """获取Tracker实例"""
        if not self._initialized:
            self.init()
        return self._tracker_instance


@register_integration('accelerate')
class AccelerateIntegration(TrackerIntegration):
    """Hugging Face Accelerate集成"""
    
    def _get_framework_name(self) -> str:
        return "Accelerate"
    
    def _get_framework_module_name(self) -> str:
        return "accelerate"
    
    def _get_tracker_class(self):
        """获取Accelerate的GeneralTracker类"""
        try:
            from accelerate.tracking import GeneralTracker
            from accelerate.logging import get_logger
        except ImportError:
            raise ImportError("Accelerate not found")
        
        logger = get_logger(__name__)
        
        class SeeTrainAccelerateTracker(GeneralTracker):
            """SeeTrain Accelerate Tracker"""
            
            name = "seetrain"
            requires_logging_directory = False
            main_process_only = True
            
            def __init__(self, integration):
                super().__init__()
                self.integration = integration
                self.run = None
                self.start()
            
            def start(self):
                """启动Tracker"""
                if hasattr(self, "run") and self.run is not None:
                    return
                
                self.run = self.integration
                logger.debug(f"Initialized SeeTrain project {self.integration.project}")
                logger.debug("Make sure to log any initial configurations with `store_init_configuration` before training!")
            
            @property
            def tracker(self):
                """返回Tracker对象"""
                return self.run
            
            def store_init_configuration(self, values: dict):
                """
                记录初始配置作为超参数
                
                Args:
                    values: 要存储的初始超参数字典
                """
                self.integration.update_config(values)
                logger.debug("Stored initial configuration hyperparameters to SeeTrain")
            
            def log(self, values: dict, step: Optional[int] = None, **kwargs):
                """
                记录指标到当前运行
                
                Args:
                    values: 要记录的指标字典
                    step: 步骤数
                    **kwargs: 其他参数
                """
                self.integration.log(values, step=step, **kwargs)
                logger.debug("Successfully logged to SeeTrain")
            
            def log_images(self, values: dict, step: Optional[int] = None, **kwargs):
                """
                记录图像到当前运行
                
                Args:
                    values: 要记录的图像字典
                    step: 步骤数
                    **kwargs: 其他参数
                """
                for k, v in values.items():
                    if isinstance(v, list):
                        for i, image in enumerate(v):
                            image_key = f"{k}_{i}" if len(v) > 1 else k
                            self.integration.log_image(image_key, image, step=step, **kwargs)
                    else:
                        self.integration.log_image(k, v, step=step, **kwargs)
                logger.debug("Successfully logged images to SeeTrain")
            
            def log_audio(self, values: dict, step: Optional[int] = None, **kwargs):
                """
                记录音频到当前运行
                
                Args:
                    values: 要记录的音频字典
                    step: 步骤数
                    **kwargs: 其他参数
                """
                for k, v in values.items():
                    if isinstance(v, list):
                        for i, audio in enumerate(v):
                            audio_key = f"{k}_{i}" if len(v) > 1 else k
                            self.integration.log_audio(audio_key, audio, step=step, **kwargs)
                    else:
                        self.integration.log_audio(k, v, step=step, **kwargs)
                logger.debug("Successfully logged audio to SeeTrain")
            
            def log_text(self, values: dict, step: Optional[int] = None, **kwargs):
                """
                记录文本到当前运行
                
                Args:
                    values: 要记录的文本字典
                    step: 步骤数
                    **kwargs: 其他参数
                """
                for k, v in values.items():
                    if isinstance(v, list):
                        for i, text in enumerate(v):
                            text_key = f"{k}_{i}" if len(v) > 1 else k
                            self.integration.log_text(text_key, text, step=step)
                    else:
                        self.integration.log_text(k, v, step=step)
                logger.debug("Successfully logged text to SeeTrain")
            
            def finish(self):
                """关闭SeeTrain writer"""
                self.integration.finish()
                logger.debug("SeeTrain run closed")
        
        return lambda: SeeTrainAccelerateTracker(self)


@register_integration('ray_tune')
class RayTuneIntegration(TrackerIntegration):
    """Ray Tune集成"""
    
    def _get_framework_name(self) -> str:
        return "Ray Tune"
    
    def _get_framework_module_name(self) -> str:
        return "ray.tune"
    
    def _get_tracker_class(self):
        """获取Ray Tune的Logger类"""
        try:
            from ray.tune.logger import Logger
        except ImportError:
            raise ImportError("Ray Tune not found")
        
        class SeeTrainRayTuneLogger(Logger):
            """SeeTrain Ray Tune Logger"""
            
            def __init__(self, integration, config, logdir, trial=None):
                super().__init__(config, logdir, trial)
                self.integration = integration
                self.trial = trial
                
                # 记录配置
                if config:
                    self.integration.update_config(config)
                
                # 记录trial信息
                if trial:
                    trial_info = {
                        'trial_id': trial.trial_id,
                        'trial_name': trial.trial_name,
                        'status': trial.status
                    }
                    self.integration.update_config(trial_info)
            
            def on_result(self, result):
                """处理结果"""
                # 过滤掉Ray Tune内部指标
                filtered_result = {}
                for key, value in result.items():
                    if not key.startswith(('_', 'config', 'done', 'time')):
                        filtered_result[key] = value
                
                if filtered_result:
                    self.integration.log(filtered_result)
            
            def close(self):
                """关闭Logger"""
                self.integration.finish()
        
        return lambda: SeeTrainRayTuneLogger(self, {}, "", None)


@register_integration('optuna')
class OptunaIntegration(TrackerIntegration):
    """Optuna集成"""
    
    def _get_framework_name(self) -> str:
        return "Optuna"
    
    def _get_framework_module_name(self) -> str:
        return "optuna"
    
    def _get_tracker_class(self):
        """获取Optuna的Callback类"""
        try:
            import optuna
        except ImportError:
            raise ImportError("Optuna not found")
        
        class SeeTrainOptunaCallback:
            """SeeTrain Optuna Callback"""
            
            def __init__(self, integration):
                self.integration = integration
                self.study = None
                self.trial = None
            
            def set_study(self, study):
                """设置Study"""
                self.study = study
                study_info = {
                    'study_name': study.study_name,
                    'direction': str(study.direction),
                    'n_trials': study.n_trials
                }
                self.integration.update_config(study_info)
            
            def set_trial(self, trial):
                """设置Trial"""
                self.trial = trial
                trial_info = {
                    'trial_number': trial.number,
                    'trial_id': trial._trial_id,
                    'trial_state': trial.state.name
                }
                self.integration.update_config(trial_info)
            
            def on_trial_begin(self, study, trial):
                """Trial开始时调用"""
                self.set_study(study)
                self.set_trial(trial)
                
                # 记录超参数
                if trial.params:
                    self.integration.log({'hyperparams': trial.params})
                
                self.integration.log({'trial/status': 'started'})
            
            def on_trial_complete(self, study, trial):
                """Trial完成时调用"""
                self.set_study(study)
                self.set_trial(trial)
                
                # 记录结果
                if trial.values:
                    for i, value in enumerate(trial.values):
                        objective_name = f"objective_{i}" if len(trial.values) > 1 else "objective"
                        self.integration.log({objective_name: value})
                
                # 记录用户属性
                if trial.user_attrs:
                    self.integration.log({'user_attrs': trial.user_attrs})
                
                self.integration.log({'trial/status': 'completed'})
            
            def on_trial_fail(self, study, trial):
                """Trial失败时调用"""
                self.set_study(study)
                self.set_trial(trial)
                self.integration.log({'trial/status': 'failed'})
            
            def on_optimization_step(self, study, trial):
                """优化步骤时调用"""
                self.set_study(study)
                self.set_trial(trial)
                
                # 记录中间值
                if trial.intermediate_values:
                    for step, value in trial.intermediate_values.items():
                        self.integration.log({f'intermediate/step_{step}': value})
        
        return lambda: SeeTrainOptunaCallback(self)


@register_integration('wandb')
class WandBIntegration(TrackerIntegration):
    """WandB集成（作为Tracker使用）"""
    
    def _get_framework_name(self) -> str:
        return "WandB"
    
    def _get_framework_module_name(self) -> str:
        return "wandb"
    
    def _get_tracker_class(self):
        """获取WandB的Logger类"""
        try:
            import wandb
        except ImportError:
            raise ImportError("WandB not found")
        
        class SeeTrainWandBLogger:
            """SeeTrain WandB Logger"""
            
            def __init__(self, integration, project=None, name=None, config=None):
                self.integration = integration
                self.project = project or integration.project
                self.name = name or integration.experiment_name
                self.config = config or {}
                
                # 记录配置
                if self.config:
                    self.integration.update_config(self.config)
            
            def log(self, data, step=None, commit=True):
                """记录数据"""
                self.integration.log(data, step=step)
            
            def log_image(self, key, image, step=None, caption=None):
                """记录图像"""
                self.integration.log_image(key, image, step=step, caption=caption)
            
            def log_audio(self, key, audio, step=None, caption=None, sample_rate=None):
                """记录音频"""
                self.integration.log_audio(key, audio, step=step, 
                                         caption=caption, sample_rate=sample_rate)
            
            def log_text(self, key, text, step=None):
                """记录文本"""
                self.integration.log_text(key, text, step=step)
            
            def watch(self, model, log="gradients", log_freq=1000):
                """监控模型"""
                # SeeTrain暂不支持模型监控，记录日志
                seetrainlog.info(f"Model monitoring requested: {log}, freq: {log_freq}")
            
            def finish(self):
                """完成记录"""
                self.integration.finish()
        
        return lambda: SeeTrainWandBLogger(self)
