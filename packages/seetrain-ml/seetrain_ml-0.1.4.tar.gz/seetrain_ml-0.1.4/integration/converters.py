#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据格式转换模块

提供各种深度学习框架数据格式到SeeTrain标准格式的转换功能
"""

import os
import sys
import numpy as np
import io
from typing import Any, Dict, Optional, Union, List, Tuple
from abc import ABC, abstractmethod

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from data import Image, Audio, Text
from log import seetrainlog


class BaseConverter(ABC):
    """基础转换器"""
    
    @abstractmethod
    def convert(self, data: Any, **kwargs) -> Any:
        """转换数据，子类必须实现"""
        pass


class TensorConverter(BaseConverter):
    """张量转换器"""
    
    def convert(self, data: Any, **kwargs) -> np.ndarray:
        """将各种张量格式转换为numpy数组"""
        try:
            # PyTorch tensor
            if hasattr(data, 'detach') and hasattr(data, 'cpu'):
                return data.detach().cpu().numpy()
            
            # TensorFlow tensor
            if hasattr(data, 'numpy'):
                return data.numpy()
            
            # JAX array
            if hasattr(data, 'to_py'):
                return data.to_py()
            
            # NumPy array
            if isinstance(data, np.ndarray):
                return data
            
            # 其他情况尝试转换
            return np.array(data)
            
        except Exception as e:
            seetrainlog.error(f"Failed to convert tensor: {e}")
            return data


class ImageConverter(BaseConverter):
    """图像转换器"""
    
    def convert(self, data: Any, **kwargs) -> Image:
        """将各种图像格式转换为SeeTrain Image对象"""
        try:
            # 如果已经是Image对象，直接返回
            if isinstance(data, Image):
                return data
            
            # PIL Image
            if hasattr(data, 'save'):
                return Image(data, **kwargs)
            
            # NumPy array
            if isinstance(data, np.ndarray):
                return Image(data, **kwargs)
            
            # 文件路径
            if isinstance(data, str):
                return Image(data, **kwargs)
            
            # 字节数据
            if isinstance(data, bytes):
                return Image(data, **kwargs)
            
            # 其他情况尝试转换
            return Image(data, **kwargs)
            
        except Exception as e:
            seetrainlog.error(f"Failed to convert image: {e}")
            return data


class AudioConverter(BaseConverter):
    """音频转换器"""
    
    def convert(self, data: Any, **kwargs) -> Audio:
        """将各种音频格式转换为SeeTrain Audio对象"""
        try:
            # 如果已经是Audio对象，直接返回
            if isinstance(data, Audio):
                return data
            
            # NumPy array
            if isinstance(data, np.ndarray):
                return Audio(data, **kwargs)
            
            # 文件路径
            if isinstance(data, str):
                return Audio(data, **kwargs)
            
            # 字节数据
            if isinstance(data, bytes):
                return Audio(data, **kwargs)
            
            # 其他情况尝试转换
            return Audio(data, **kwargs)
            
        except Exception as e:
            seetrainlog.error(f"Failed to convert audio: {e}")
            return data


class TextConverter(BaseConverter):
    """文本转换器"""
    
    def convert(self, data: Any, **kwargs) -> str:
        """将各种文本格式转换为字符串"""
        try:
            # 如果已经是字符串，直接返回
            if isinstance(data, str):
                return data
            
            # 字节数据
            if isinstance(data, bytes):
                return data.decode('utf-8')
            
            # 其他情况转换为字符串
            return str(data)
            
        except Exception as e:
            seetrainlog.error(f"Failed to convert text: {e}")
            return str(data)


class MetricsConverter(BaseConverter):
    """指标转换器"""
    
    def __init__(self):
        self.tensor_converter = TensorConverter()
        self.image_converter = ImageConverter()
        self.audio_converter = AudioConverter()
        self.text_converter = TextConverter()
    
    def convert(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """转换指标数据"""
        converted_data = {}
        
        for key, value in data.items():
            try:
                # 根据值类型选择转换器
                if self._is_image_data(value):
                    converted_data[key] = self.image_converter.convert(value, **kwargs)
                elif self._is_audio_data(value):
                    converted_data[key] = self.audio_converter.convert(value, **kwargs)
                elif self._is_text_data(value):
                    converted_data[key] = self.text_converter.convert(value, **kwargs)
                elif self._is_tensor_data(value):
                    converted_data[key] = self.tensor_converter.convert(value, **kwargs)
                else:
                    # 其他类型直接使用
                    converted_data[key] = value
                    
            except Exception as e:
                seetrainlog.error(f"Failed to convert metric {key}: {e}")
                converted_data[key] = value
        
        return converted_data
    
    def _is_image_data(self, value: Any) -> bool:
        """判断是否为图像数据"""
        # PIL Image
        if hasattr(value, 'save'):
            return True
        
        # NumPy array with image-like shape
        if isinstance(value, np.ndarray):
            if len(value.shape) in [2, 3] and value.shape[-1] in [1, 3, 4]:
                return True
        
        # 文件路径
        if isinstance(value, str) and any(ext in value.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            return True
        
        return False
    
    def _is_audio_data(self, value: Any) -> bool:
        """判断是否为音频数据"""
        # NumPy array with audio-like shape
        if isinstance(value, np.ndarray):
            if len(value.shape) in [1, 2]:
                return True
        
        # 文件路径
        if isinstance(value, str) and any(ext in value.lower() for ext in ['.wav', '.mp3', '.flac', '.m4a']):
            return True
        
        return False
    
    def _is_text_data(self, value: Any) -> bool:
        """判断是否为文本数据"""
        return isinstance(value, (str, bytes))
    
    def _is_tensor_data(self, value: Any) -> bool:
        """判断是否为张量数据"""
        # PyTorch tensor
        if hasattr(value, 'detach') and hasattr(value, 'cpu'):
            return True
        
        # TensorFlow tensor
        if hasattr(value, 'numpy'):
            return True
        
        # JAX array
        if hasattr(value, 'to_py'):
            return True
        
        return False


class ConfigConverter(BaseConverter):
    """配置转换器"""
    
    def convert(self, data: Any, **kwargs) -> Dict[str, Any]:
        """转换配置数据"""
        try:
            # 字典类型
            if isinstance(data, dict):
                return self._flatten_dict(data)
            
            # Namespace对象
            if hasattr(data, '__dict__'):
                return self._flatten_dict(data.__dict__)
            
            # 其他类型转换为字符串
            return {'config': str(data)}
            
        except Exception as e:
            seetrainlog.error(f"Failed to convert config: {e}")
            return {'config': str(data)}
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '/') -> Dict[str, Any]:
        """扁平化嵌套字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # 处理列表
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", v))
            else:
                items.append((new_key, v))
        return dict(items)


class FrameworkSpecificConverter:
    """框架特定转换器"""
    
    def __init__(self):
        self.metrics_converter = MetricsConverter()
        self.config_converter = ConfigConverter()
    
    def convert_pytorch_lightning_logs(self, logs: Dict[str, Any]) -> Dict[str, Any]:
        """转换PyTorch Lightning日志"""
        converted = {}
        
        for key, value in logs.items():
            # 添加前缀
            if not key.startswith('pytorch_lightning/'):
                new_key = f"pytorch_lightning/{key}"
            else:
                new_key = key
            
            # 转换值
            if isinstance(value, (int, float)):
                converted[new_key] = value
            else:
                converted[new_key] = self.metrics_converter.convert({new_key: value})[new_key]
        
        return converted
    
    def convert_keras_logs(self, logs: Dict[str, Any]) -> Dict[str, Any]:
        """转换Keras日志"""
        converted = {}
        
        for key, value in logs.items():
            # 添加前缀
            if not key.startswith('keras/'):
                new_key = f"keras/{key}"
            else:
                new_key = key
            
            # 转换值
            if isinstance(value, (int, float)):
                converted[new_key] = value
            else:
                converted[new_key] = self.metrics_converter.convert({new_key: value})[new_key]
        
        return converted
    
    def convert_transformers_logs(self, logs: Dict[str, Any]) -> Dict[str, Any]:
        """转换Transformers日志"""
        converted = {}
        
        for key, value in logs.items():
            # 添加前缀
            if not key.startswith('transformers/'):
                new_key = f"transformers/{key}"
            else:
                new_key = key
            
            # 转换值
            if isinstance(value, (int, float)):
                converted[new_key] = value
            else:
                converted[new_key] = self.metrics_converter.convert({new_key: value})[new_key]
        
        return converted
    
    def convert_mmengine_logs(self, logs: Dict[str, Any]) -> Dict[str, Any]:
        """转换MMEngine日志"""
        converted = {}
        
        for key, value in logs.items():
            # 添加前缀
            if not key.startswith('mmengine/'):
                new_key = f"mmengine/{key}"
            else:
                new_key = key
            
            # 转换值
            if isinstance(value, (int, float)):
                converted[new_key] = value
            else:
                converted[new_key] = self.metrics_converter.convert({new_key: value})[new_key]
        
        return converted


# 全局转换器实例
tensor_converter = TensorConverter()
image_converter = ImageConverter()
audio_converter = AudioConverter()
text_converter = TextConverter()
metrics_converter = MetricsConverter()
config_converter = ConfigConverter()
framework_converter = FrameworkSpecificConverter()


def convert_tensor(data: Any, **kwargs) -> np.ndarray:
    """转换张量"""
    return tensor_converter.convert(data, **kwargs)


def convert_image(data: Any, **kwargs) -> Image:
    """转换图像"""
    return image_converter.convert(data, **kwargs)


def convert_audio(data: Any, **kwargs) -> Audio:
    """转换音频"""
    return audio_converter.convert(data, **kwargs)


def convert_text(data: Any, **kwargs) -> str:
    """转换文本"""
    return text_converter.convert(data, **kwargs)


def convert_metrics(data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """转换指标"""
    return metrics_converter.convert(data, **kwargs)


def convert_config(data: Any, **kwargs) -> Dict[str, Any]:
    """转换配置"""
    return config_converter.convert(data, **kwargs)
