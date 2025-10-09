#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisBackend模式集成

适用于MMEngine, MMDetection等框架
通过注册为框架的可视化后端，实现框架的可视化接口，将可视化数据转换为SeeTrain格式
"""

import os
import sys
from typing import Any, Dict, Optional, Union, List, Sequence
from abc import ABC, abstractmethod

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from .base import BaseIntegration
from .utils import get_module, register_integration, flatten_dict
from log import seetrainlog


class VisBackendIntegration(BaseIntegration, ABC):
    """VisBackend模式基础集成类"""
    
    def __init__(self, save_dir: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.save_dir = save_dir
        self._backend_instance = None
        self._framework_module = None
        self._env_initialized = False
    
    @abstractmethod
    def _get_backend_class(self):
        """获取框架的VisBackend基类，子类必须实现"""
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
        
        # 创建VisBackend实例
        self._create_backend_instance()
    
    def _create_backend_instance(self) -> None:
        """创建VisBackend实例"""
        backend_class = self._get_backend_class()
        self._backend_instance = backend_class()
        seetrainlog.debug(f"Created visbackend instance: {backend_class.__name__}")
    
    def get_backend(self):
        """获取VisBackend实例"""
        if not self._initialized:
            self.init()
        return self._backend_instance
    
    def _force_init_env(self, func):
        """强制初始化环境的装饰器"""
        def wrapper(*args, **kwargs):
            if not self._env_initialized:
                self._init_env()
            return func(*args, **kwargs)
        return wrapper
    
    def _init_env(self) -> None:
        """初始化环境"""
        if self._env_initialized:
            return
        
        # 设置保存目录
        if self.save_dir and not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)
        
        # 初始化SeeTrain
        self.init()
        self._env_initialized = True


@register_integration('mmengine')
class MMEngineIntegration(VisBackendIntegration):
    """MMEngine集成"""
    
    def _get_framework_name(self) -> str:
        return "MMEngine"
    
    def _get_framework_module_name(self) -> str:
        return "mmengine"
    
    def _get_backend_class(self):
        """获取MMEngine的BaseVisBackend类"""
        try:
            from mmengine.registry import VISBACKENDS
            from mmengine.visualization.vis_backend import BaseVisBackend
            from mmengine.config import Config
        except ImportError:
            raise ImportError("MMEngine not found")
        
        @VISBACKENDS.register_module()
        class SeeTrainMMEngineVisBackend(BaseVisBackend):
            """SeeTrain MMEngine VisBackend"""
            
            def __init__(self, save_dir: str = None, init_kwargs: Optional[dict] = None):
                super().__init__(save_dir)
                self._save_dir = save_dir
                self._init_kwargs = init_kwargs or {}
                self._env_initialized = False
                self._integration = None
            
            def _init_env(self) -> Any:
                """初始化环境"""
                if self._env_initialized:
                    return self._integration
                
                # 创建集成实例
                integration_kwargs = self._init_kwargs.copy()
                integration_kwargs['save_dir'] = self._save_dir
                
                self._integration = MMEngineIntegration(**integration_kwargs)
                self._integration.init()
                
                self._env_initialized = True
                return self._integration
            
            @property
            def experiment(self) -> Any:
                """返回实验对象"""
                return self._init_env()
            
            def add_config(self, config, **kwargs) -> None:
                """记录配置"""
                integration = self._init_env()
                
                def repack_dict(a, prefix=""):
                    """解包嵌套字典"""
                    new_dict = dict()
                    for key, value in a.items():
                        key = str(key)
                        if isinstance(value, dict):
                            if prefix != "":
                                new_dict.update(repack_dict(value, f"{prefix}/{key}"))
                            else:
                                new_dict.update(repack_dict(value, key))
                        elif isinstance(value, list) or isinstance(value, tuple):
                            if all(not isinstance(element, dict) for element in value):
                                new_dict[key] = value
                            else:
                                for i, item in enumerate(value):
                                    new_dict.update(repack_dict(item, f"{key}[{i}]"))
                        elif prefix != "":
                            new_dict[f"{prefix}/{key}"] = value
                        else:
                            new_dict[key] = value
                    return new_dict
                
                if hasattr(config, 'to_dict'):
                    config_dict = config.to_dict()
                else:
                    config_dict = config
                
                flattened_config = repack_dict(config_dict)
                integration.update_config(flattened_config)
            
            def add_graph(self, model, data_batch: Sequence[dict], **kwargs) -> None:
                """记录模型图"""
                # MMEngine暂不支持模型图记录
                seetrainlog.info("Model graph logging not supported in MMEngine integration")
            
            def add_image(self, name: str, image, step: int = 0, **kwargs) -> None:
                """记录图像"""
                integration = self._init_env()
                integration.log_image(name, image, step=step, **kwargs)
            
            def add_scalar(self, name: str, value: Union[int, float], step: int = 0, **kwargs) -> None:
                """记录标量"""
                integration = self._init_env()
                integration.log_scalar(name, value, step=step)
            
            def add_scalars(self, scalar_dict: dict, step: int = 0, **kwargs) -> None:
                """记录多个标量"""
                integration = self._init_env()
                integration.log(scalar_dict, step=step)
            
            def add_histogram(self, name: str, values, step: int = 0, **kwargs) -> None:
                """记录直方图"""
                integration = self._init_env()
                # 将直方图数据转换为图像
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    plt.figure(figsize=(8, 6))
                    plt.hist(values, bins=50, alpha=0.7)
                    plt.title(f"Histogram: {name}")
                    plt.xlabel("Value")
                    plt.ylabel("Frequency")
                    
                    # 转换为图像
                    import io
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                    buf.seek(0)
                    
                    integration.log_image(f"histogram/{name}", buf.getvalue(), step=step)
                    plt.close()
                except ImportError:
                    seetrainlog.warning("matplotlib not available for histogram logging")
            
            def add_text(self, name: str, text: str, step: int = 0, **kwargs) -> None:
                """记录文本"""
                integration = self._init_env()
                integration.log_text(name, text, step=step)
            
            def add_audio(self, name: str, audio, step: int = 0, **kwargs) -> None:
                """记录音频"""
                integration = self._init_env()
                integration.log_audio(name, audio, step=step, **kwargs)
            
            def add_video(self, name: str, video, step: int = 0, **kwargs) -> None:
                """记录视频"""
                integration = self._init_env()
                # 将视频转换为图像序列
                try:
                    import cv2
                    import numpy as np
                    
                    if isinstance(video, str):
                        cap = cv2.VideoCapture(video)
                    else:
                        cap = video
                    
                    frame_count = 0
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        frame_name = f"{name}/frame_{frame_count:04d}"
                        integration.log_image(frame_name, frame, step=step)
                        frame_count += 1
                    
                    if isinstance(video, str):
                        cap.release()
                except ImportError:
                    seetrainlog.warning("opencv not available for video logging")
            
            def close(self) -> None:
                """关闭VisBackend"""
                if self._integration:
                    self._integration.finish()
        
        return SeeTrainMMEngineVisBackend


@register_integration('tensorboard')
class TensorBoardIntegration(VisBackendIntegration):
    """TensorBoard集成（作为VisBackend使用）"""
    
    def _get_framework_name(self) -> str:
        return "TensorBoard"
    
    def _get_framework_module_name(self) -> str:
        return "tensorboard"
    
    def _get_backend_class(self):
        """获取TensorBoard的SummaryWriter类"""
        try:
            from torch.utils.tensorboard import SummaryWriter
        except ImportError:
            try:
                from tensorboardX import SummaryWriter
            except ImportError:
                raise ImportError("TensorBoard not found")
        
        class SeeTrainTensorBoardBackend:
            """SeeTrain TensorBoard Backend"""
            
            def __init__(self, log_dir=None, **kwargs):
                self.log_dir = log_dir
                self.integration = TensorBoardIntegration(**kwargs)
                self.integration.init()
            
            def add_scalar(self, tag, scalar_value, global_step=None, walltime=None):
                """添加标量"""
                self.integration.log_scalar(tag, scalar_value, step=global_step)
            
            def add_scalars(self, main_tag, tag_scalar_dict, global_step=None, walltime=None):
                """添加多个标量"""
                scalars = {f"{main_tag}/{tag}": value for tag, value in tag_scalar_dict.items()}
                self.integration.log(scalars, step=global_step)
            
            def add_histogram(self, tag, values, global_step=None, bins='tensorflow', walltime=None):
                """添加直方图"""
                self.integration.log_image(f"histogram/{tag}", values, step=global_step)
            
            def add_image(self, tag, img_tensor, global_step=None, walltime=None):
                """添加图像"""
                self.integration.log_image(tag, img_tensor, step=global_step)
            
            def add_images(self, tag, img_tensor, global_step=None, walltime=None):
                """添加多个图像"""
                for i, img in enumerate(img_tensor):
                    self.integration.log_image(f"{tag}_{i}", img, step=global_step)
            
            def add_figure(self, tag, figure, global_step=None, close=True, walltime=None):
                """添加图形"""
                self.integration.log_image(tag, figure, step=global_step)
            
            def add_text(self, tag, text_string, global_step=None, walltime=None):
                """添加文本"""
                self.integration.log_text(tag, text_string, step=global_step)
            
            def add_audio(self, tag, snd_tensor, global_step=None, sample_rate=44100, walltime=None):
                """添加音频"""
                self.integration.log_audio(tag, snd_tensor, step=global_step, sample_rate=sample_rate)
            
            def add_video(self, tag, vid_tensor, global_step=None, fps=4, walltime=None):
                """添加视频"""
                self.integration.log_image(f"video/{tag}", vid_tensor, step=global_step)
            
            def add_graph(self, model, input_to_model=None, verbose=False):
                """添加模型图"""
                seetrainlog.info("Model graph logging not supported in TensorBoard integration")
            
            def flush(self):
                """刷新"""
                pass
            
            def close(self):
                """关闭"""
                self.integration.finish()
        
        return SeeTrainTensorBoardBackend


@register_integration('mlflow')
class MLflowIntegration(VisBackendIntegration):
    """MLflow集成（作为VisBackend使用）"""
    
    def _get_framework_name(self) -> str:
        return "MLflow"
    
    def _get_framework_module_name(self) -> str:
        return "mlflow"
    
    def _get_backend_class(self):
        """获取MLflow的Tracking类"""
        try:
            import mlflow
        except ImportError:
            raise ImportError("MLflow not found")
        
        class SeeTrainMLflowBackend:
            """SeeTrain MLflow Backend"""
            
            def __init__(self, tracking_uri=None, **kwargs):
                self.tracking_uri = tracking_uri
                self.integration = MLflowIntegration(**kwargs)
                self.integration.init()
                
                # 设置MLflow跟踪URI
                if tracking_uri:
                    mlflow.set_tracking_uri(tracking_uri)
            
            def log_param(self, key, value):
                """记录参数"""
                self.integration.update_config({key: value})
            
            def log_params(self, params):
                """记录多个参数"""
                self.integration.update_config(params)
            
            def log_metric(self, key, value, step=None):
                """记录指标"""
                self.integration.log_scalar(key, value, step=step)
            
            def log_metrics(self, metrics, step=None):
                """记录多个指标"""
                self.integration.log(metrics, step=step)
            
            def log_image(self, artifact, image):
                """记录图像"""
                self.integration.log_image(artifact, image)
            
            def log_text(self, artifact, text):
                """记录文本"""
                self.integration.log_text(artifact, text)
            
            def log_artifact(self, local_path, artifact_path=None):
                """记录文件"""
                try:
                    with open(local_path, 'rb') as f:
                        file_data = f.read()
                    
                    filename = artifact_path or os.path.basename(local_path)
                    self.integration.log_image(f"artifact/{filename}", file_data)
                except Exception as e:
                    seetrainlog.error(f"Failed to log artifact {local_path}: {e}")
            
            def log_artifacts(self, local_dir, artifact_path=None):
                """记录多个文件"""
                for root, dirs, files in os.walk(local_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, local_dir)
                        artifact_name = f"{artifact_path}/{rel_path}" if artifact_path else rel_path
                        self.log_artifact(file_path, artifact_name)
            
            def set_tag(self, key, value):
                """设置标签"""
                self.integration.tags.append(f"{key}:{value}")
            
            def set_tags(self, tags):
                """设置多个标签"""
                for key, value in tags.items():
                    self.set_tag(key, value)
            
            def end_run(self):
                """结束运行"""
                self.integration.finish()
        
        return SeeTrainMLflowBackend
