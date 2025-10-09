#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Callback模式集成

适用于PyTorch Lightning, Keras, Transformers, Ultralytics等框架
通过继承框架的回调基类，重写关键方法来实现自动日志记录
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
from .utils import get_module, check_version_compatibility, register_integration
from log import seetrainlog


class CallbackIntegration(BaseIntegration, ABC):
    """Callback模式基础集成类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._callback_instance = None
        self._framework_module = None
    
    @abstractmethod
    def _get_callback_class(self):
        """获取框架的回调基类，子类必须实现"""
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
        
        # 检查版本兼容性
        if not self._check_version_compatibility():
            seetrainlog.warning(f"Version compatibility check failed for {module_name}")
        
        # 创建回调实例
        self._create_callback_instance()
    
    def _check_version_compatibility(self) -> bool:
        """检查版本兼容性，子类可以重写"""
        return True
    
    def _create_callback_instance(self) -> None:
        """创建回调实例"""
        callback_class = self._get_callback_class()
        self._callback_instance = callback_class()
        seetrainlog.debug(f"Created callback instance: {callback_class.__name__}")
    
    def get_callback(self):
        """获取回调实例"""
        if not self._initialized:
            self.init()
        return self._callback_instance


@register_integration('pytorch_lightning')
class PyTorchLightningIntegration(CallbackIntegration):
    """PyTorch Lightning集成"""
    
    def _get_framework_name(self) -> str:
        return "PyTorch Lightning"
    
    def _get_framework_module_name(self) -> str:
        return "lightning"
    
    def _get_callback_class(self):
        """获取PyTorch Lightning的Logger类"""
        try:
            # 尝试导入新版本的lightning
            from lightning.pytorch.loggers.logger import Logger
            return self._create_lightning_logger()
        except ImportError:
            try:
                # 尝试导入旧版本的pytorch_lightning
                from pytorch_lightning.loggers.logger import Logger
                return self._create_lightning_logger()
            except ImportError:
                raise ImportError("PyTorch Lightning not found")
    
    def _create_lightning_logger(self):
        """创建Lightning Logger类"""
        
        class SeeTrainLightningLogger:
            """SeeTrain Lightning Logger"""
            
            def __init__(self, integration):
                self.integration = integration
                self._experiment = None
            
            @property
            def experiment(self):
                """实验对象"""
                if self._experiment is None:
                    self._experiment = self.integration
                return self._experiment
            
            @property
            def name(self):
                """Logger名称"""
                return self.integration.project or "SeeTrain"
            
            @property
            def version(self):
                """版本"""
                return "1.0.0"
            
            def log_hyperparams(self, params):
                """记录超参数"""
                if isinstance(params, dict):
                    self.integration.update_config(params)
                else:
                    # 处理Namespace对象
                    if hasattr(params, '__dict__'):
                        self.integration.update_config(params.__dict__)
            
            def log_metrics(self, metrics, step=None):
                """记录指标"""
                self.integration.log(metrics, step=step)
            
            def log_image(self, key, images, step=None, **kwargs):
                """记录图像"""
                if not isinstance(images, list):
                    images = [images]
                
                for i, image in enumerate(images):
                    image_key = f"{key}_{i}" if len(images) > 1 else key
                    self.integration.log_image(image_key, image, step=step, **kwargs)
            
            def log_audio(self, key, audios, step=None, **kwargs):
                """记录音频"""
                if not isinstance(audios, list):
                    audios = [audios]
                
                for i, audio in enumerate(audios):
                    audio_key = f"{key}_{i}" if len(audios) > 1 else key
                    self.integration.log_audio(audio_key, audio, step=step, **kwargs)
            
            def log_text(self, key, texts, step=None, **kwargs):
                """记录文本"""
                if not isinstance(texts, list):
                    texts = [texts]
                
                for i, text in enumerate(texts):
                    text_key = f"{key}_{i}" if len(texts) > 1 else key
                    self.integration.log_text(text_key, text, step=step)
            
            def finalize(self, status):
                """完成日志记录"""
                if status == "success":
                    self.integration.finish()
        
        return lambda: SeeTrainLightningLogger(self)


@register_integration('keras')
class KerasIntegration(CallbackIntegration):
    """Keras集成"""
    
    def _get_framework_name(self) -> str:
        return "Keras"
    
    def _get_framework_module_name(self) -> str:
        # 优先尝试tensorflow.keras
        try:
            import tensorflow as tf
            if hasattr(tf, 'keras'):
                return "tensorflow.keras"
        except ImportError:
            pass
        
        # 回退到独立的keras
        return "keras"
    
    def _get_callback_class(self):
        """获取Keras的Callback类"""
        try:
            from tensorflow.keras.callbacks import Callback
        except ImportError:
            try:
                from keras.callbacks import Callback
            except ImportError:
                raise ImportError("Keras not found")
        
        class SeeTrainKerasCallback(Callback):
            """SeeTrain Keras Callback"""
            
            def __init__(self, integration):
                super().__init__()
                self.integration = integration
                self.global_step = 0
            
            def on_train_begin(self, logs=None):
                """训练开始时调用"""
                logs = logs or {}
                self.integration.log({'training/status': 'started'})
                seetrainlog.info("Keras training started")
            
            def on_train_end(self, logs=None):
                """训练结束时调用"""
                logs = logs or {}
                self.integration.log({'training/status': 'completed'})
                seetrainlog.info("Keras training completed")
            
            def on_epoch_begin(self, epoch, logs=None):
                """Epoch开始时调用"""
                logs = logs or {}
                self.integration.log({'epoch/epoch': epoch, 'epoch/status': 'started'})
            
            def on_epoch_end(self, epoch, logs=None):
                """Epoch结束时调用"""
                logs = logs or {}
                
                # 添加epoch前缀
                epoch_logs = {f"epoch/{k}": v for k, v in logs.items()}
                epoch_logs['epoch/epoch'] = epoch
                
                # 记录学习率
                if hasattr(self.model, 'optimizer') and hasattr(self.model.optimizer, 'learning_rate'):
                    lr = self.model.optimizer.learning_rate
                    if hasattr(lr, 'numpy'):
                        epoch_logs['epoch/learning_rate'] = float(lr.numpy())
                    else:
                        epoch_logs['epoch/learning_rate'] = float(lr)
                
                self.integration.log(epoch_logs)
            
            def on_batch_begin(self, batch, logs=None):
                """Batch开始时调用"""
                logs = logs or {}
                self.global_step += 1
            
            def on_batch_end(self, batch, logs=None):
                """Batch结束时调用"""
                logs = logs or {}
                
                # 添加batch前缀
                batch_logs = {f"batch/{k}": v for k, v in logs.items()}
                batch_logs['batch/global_step'] = self.global_step
                
                self.integration.log(batch_logs)
            
            def on_train_batch_end(self, batch, logs=None):
                """训练batch结束时调用"""
                self.on_batch_end(batch, logs)
            
            def on_test_begin(self, logs=None):
                """测试开始时调用"""
                logs = logs or {}
                self.integration.log({'testing/status': 'started'})
            
            def on_test_end(self, logs=None):
                """测试结束时调用"""
                logs = logs or {}
                test_logs = {f"test/{k}": v for k, v in logs.items()}
                self.integration.log(test_logs)
            
            def on_predict_begin(self, logs=None):
                """预测开始时调用"""
                logs = logs or {}
                self.integration.log({'prediction/status': 'started'})
            
            def on_predict_end(self, logs=None):
                """预测结束时调用"""
                logs = logs or {}
                self.integration.log({'prediction/status': 'completed'})
        
        return lambda: SeeTrainKerasCallback(self)


@register_integration('transformers')
class TransformersIntegration(CallbackIntegration):
    """Transformers集成"""
    
    def _get_framework_name(self) -> str:
        return "Transformers"
    
    def _get_framework_module_name(self) -> str:
        return "transformers"
    
    def _get_callback_class(self):
        """获取Transformers的TrainerCallback类"""
        try:
            from transformers import TrainerCallback
        except ImportError:
            raise ImportError("Transformers not found")
        
        class SeeTrainTransformersCallback(TrainerCallback):
            """SeeTrain Transformers Callback"""
            
            def __init__(self, integration):
                super().__init__()
                self.integration = integration
            
            def on_train_begin(self, args, state, control, **kwargs):
                """训练开始时调用"""
                self.integration.log({'training/status': 'started'})
                self.integration.update_config(args.to_dict())
                seetrainlog.info("Transformers training started")
            
            def on_train_end(self, args, state, control, **kwargs):
                """训练结束时调用"""
                self.integration.log({'training/status': 'completed'})
                seetrainlog.info("Transformers training completed")
            
            def on_epoch_begin(self, args, state, control, **kwargs):
                """Epoch开始时调用"""
                self.integration.log({
                    'epoch/epoch': state.epoch,
                    'epoch/status': 'started'
                })
            
            def on_epoch_end(self, args, state, control, **kwargs):
                """Epoch结束时调用"""
                self.integration.log({
                    'epoch/epoch': state.epoch,
                    'epoch/status': 'completed'
                })
            
            def on_step_begin(self, args, state, control, **kwargs):
                """Step开始时调用"""
                pass
            
            def on_step_end(self, args, state, control, **kwargs):
                """Step结束时调用"""
                # 记录训练指标
                if hasattr(state, 'log_history') and state.log_history:
                    latest_log = state.log_history[-1]
                    if 'train_loss' in latest_log:
                        self.integration.log({
                            'step/global_step': state.global_step,
                            'step/train_loss': latest_log['train_loss']
                        })
            
            def on_evaluate(self, args, state, control, **kwargs):
                """评估时调用"""
                if hasattr(state, 'log_history') and state.log_history:
                    latest_log = state.log_history[-1]
                    eval_logs = {f"eval/{k}": v for k, v in latest_log.items() 
                               if k.startswith('eval_')}
                    if eval_logs:
                        self.integration.log(eval_logs)
            
            def on_log(self, args, state, control, **kwargs):
                """日志记录时调用"""
                if hasattr(state, 'log_history') and state.log_history:
                    latest_log = state.log_history[-1]
                    # 过滤掉已处理的指标
                    filtered_logs = {k: v for k, v in latest_log.items() 
                                   if not k.startswith(('train_', 'eval_'))}
                    if filtered_logs:
                        self.integration.log(filtered_logs)
        
        return lambda: SeeTrainTransformersCallback(self)


@register_integration('ultralytics')
class UltralyticsIntegration(CallbackIntegration):
    """Ultralytics集成"""
    
    def _get_framework_name(self) -> str:
        return "Ultralytics"
    
    def _get_framework_module_name(self) -> str:
        return "ultralytics"
    
    def _get_callback_class(self):
        """获取Ultralytics的回调类"""
        try:
            from ultralytics.utils.callbacks import default_callbacks
        except ImportError:
            raise ImportError("Ultralytics not found")
        
        class SeeTrainUltralyticsCallback:
            """SeeTrain Ultralytics Callback"""
            
            def __init__(self, integration):
                self.integration = integration
            
            def on_pretrain_routine_start(self, trainer):
                """预训练例程开始时调用"""
                self.integration.log({'training/status': 'pretrain_started'})
                seetrainlog.info("Ultralytics pretrain started")
            
            def on_train_start(self, trainer):
                """训练开始时调用"""
                self.integration.log({'training/status': 'started'})
                seetrainlog.info("Ultralytics training started")
            
            def on_train_epoch_start(self, trainer):
                """训练epoch开始时调用"""
                self.integration.log({
                    'epoch/epoch': trainer.epoch,
                    'epoch/status': 'started'
                })
            
            def on_train_epoch_end(self, trainer):
                """训练epoch结束时调用"""
                # 记录训练指标
                metrics = {}
                if hasattr(trainer, 'metrics'):
                    for key, value in trainer.metrics.items():
                        if isinstance(value, (int, float)):
                            metrics[f"train/{key}"] = value
                
                metrics['epoch/epoch'] = trainer.epoch
                self.integration.log(metrics)
            
            def on_val_start(self, trainer):
                """验证开始时调用"""
                self.integration.log({'validation/status': 'started'})
            
            def on_val_end(self, trainer):
                """验证结束时调用"""
                # 记录验证指标
                metrics = {}
                if hasattr(trainer, 'validator') and hasattr(trainer.validator, 'metrics'):
                    for key, value in trainer.validator.metrics.items():
                        if isinstance(value, (int, float)):
                            metrics[f"val/{key}"] = value
                
                if metrics:
                    self.integration.log(metrics)
            
            def on_train_end(self, trainer):
                """训练结束时调用"""
                self.integration.log({'training/status': 'completed'})
                seetrainlog.info("Ultralytics training completed")
            
            def on_predict_start(self, trainer):
                """预测开始时调用"""
                self.integration.log({'prediction/status': 'started'})
            
            def on_predict_end(self, trainer):
                """预测结束时调用"""
                self.integration.log({'prediction/status': 'completed'})
        
        return lambda: SeeTrainUltralyticsCallback(self)
