#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础集成类

定义了所有集成模式的通用接口和基础功能
"""

import os
import sys
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List, Callable
from datetime import datetime

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from sync.metrics import get_consumer, start_consumer
from log import seetrainlog


class BaseIntegration(ABC):
    """基础集成类，定义所有集成模式的通用接口"""
    
    def __init__(self, 
                 project: Optional[str] = None,
                 experiment_name: Optional[str] = None,
                 description: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 **kwargs):
        """
        初始化基础集成
        
        Args:
            project: 项目名称
            experiment_name: 实验名称
            description: 实验描述
            tags: 标签列表
            **kwargs: 其他参数
        """
        self.project = project
        self.experiment_name = experiment_name
        self.description = description
        self.tags = tags or []
        self.kwargs = kwargs
        
        # 框架标识
        self.framework_name = self._get_framework_name()
        self.tags.append(f"🔧{self.framework_name}")
        
        # 初始化状态
        self._initialized = False
        self._lock = threading.Lock()
        
        # 配置管理
        self._config = {}
        
        # 统计信息
        self._stats = {
            'total_logs': 0,
            'total_errors': 0,
            'start_time': None,
            'last_log_time': None
        }
    
    @abstractmethod
    def _get_framework_name(self) -> str:
        """获取框架名称，子类必须实现"""
        pass
    
    @abstractmethod
    def _initialize_framework(self) -> None:
        """初始化框架特定的功能，子类必须实现"""
        pass
    
    def init(self) -> 'BaseIntegration':
        """初始化集成"""
        with self._lock:
            if self._initialized:
                seetrainlog.warning(f"{self.framework_name} 集成已经初始化")
                return self
            
            try:
                # 设置框架标识
                self._set_framework_config()
                
                # 初始化框架特定功能
                self._initialize_framework()
                
                # 启动指标消费者
                start_consumer()
                
                # 更新统计信息
                self._stats['start_time'] = datetime.now()
                self._initialized = True
                
                seetrainlog.info(f"{self.framework_name} 集成初始化成功")
                
            except Exception as e:
                seetrainlog.error(f"{self.framework_name} 集成初始化失败: {e}")
                raise
        
        return self
    
    def _set_framework_config(self) -> None:
        """设置框架配置"""
        self._config.update({
            'FRAMEWORK': self.framework_name,
            'PROJECT': self.project,
            'EXPERIMENT_NAME': self.experiment_name,
            'DESCRIPTION': self.description,
            'TAGS': self.tags,
            'INIT_TIME': datetime.now().isoformat()
        })
    
    def log(self, data: Dict[str, Any], step: Optional[int] = None) -> None:
        """
        记录数据
        
        Args:
            data: 要记录的数据字典
            step: 步骤数
        """
        if not self._initialized:
            seetrainlog.warning(f"{self.framework_name} 集成未初始化，跳过日志记录")
            return
        
        try:
            # 添加框架前缀
            prefixed_data = self._add_framework_prefix(data)
            
            # 记录到指标队列
            from sync.metrics import get_queue
            queue = get_queue()
            with threading.Lock():
                queue.add_metrics_dict(prefixed_data, step=step)
            
            # 更新统计信息
            self._stats['total_logs'] += len(prefixed_data)
            self._stats['last_log_time'] = datetime.now()
            
            seetrainlog.debug(f"{self.framework_name} 记录 {len(prefixed_data)} 个指标")
            
        except Exception as e:
            self._stats['total_errors'] += 1
            seetrainlog.error(f"{self.framework_name} 记录指标失败: {e}")
    
    def _add_framework_prefix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """为指标添加框架前缀"""
        prefixed_data = {}
        for key, value in data.items():
            # 如果key已经包含框架前缀，则不重复添加
            if key.startswith(f"{self.framework_name.lower()}/"):
                prefixed_data[key] = value
            else:
                prefixed_data[f"{self.framework_name.lower()}/{key}"] = value
        
        return prefixed_data
    
    def log_scalar(self, name: str, value: Union[int, float], step: Optional[int] = None) -> None:
        """记录标量值"""
        self.log({name: value}, step=step)
    
    def log_image(self, name: str, image: Any, step: Optional[int] = None, **kwargs) -> None:
        """记录图像"""
        from data import Image
        try:
            if not isinstance(image, Image):
                image = Image(image, **kwargs)
            self.log({name: image}, step=step)
        except Exception as e:
            seetrainlog.error(f"记录图像失败: {e}")
    
    def log_audio(self, name: str, audio: Any, step: Optional[int] = None, **kwargs) -> None:
        """记录音频"""
        from data import Audio
        try:
            if not isinstance(audio, Audio):
                audio = Audio(audio, **kwargs)
            self.log({name: audio}, step=step)
        except Exception as e:
            seetrainlog.error(f"记录音频失败: {e}")
    
    def log_text(self, name: str, text: str, step: Optional[int] = None) -> None:
        """记录文本"""
        self.log({name: text}, step=step)
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """更新配置"""
        self._config.update(config)
        seetrainlog.debug(f"{self.framework_name} 配置已更新")
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self._config.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self._stats.copy()
        if self._stats['start_time']:
            stats['uptime'] = (datetime.now() - self._stats['start_time']).total_seconds()
        return stats
    
    def finish(self) -> None:
        """完成集成，清理资源"""
        if not self._initialized:
            return
        
        try:
            # 记录最终统计信息
            final_stats = self.get_stats()
            self.log({'integration/final_stats': final_stats})
            
            # 等待指标处理完成
            time.sleep(1.0)
            
            seetrainlog.info(f"{self.framework_name} 集成已完成")
            
        except Exception as e:
            seetrainlog.error(f"{self.framework_name} 集成完成时发生错误: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self.init()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.finish()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(framework={self.framework_name}, initialized={self._initialized})"
