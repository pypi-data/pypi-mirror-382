#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 媒体文件处理模块

import sys
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ..api import OpenAPI
from ..api.types import Metric as APIMetric
from ..data import Image, Audio, Video
from ..log import seetrainlog
from .types import MetricType, FileTypeMapping
from .qm import Metric


class MediaHandler:
    """媒体文件处理器"""

    def __init__(self, api: OpenAPI, task_id: str):
        """
        初始化媒体处理器
        
        Args:
            api: API客户端实例
            task_id: 任务ID
        """
        self.api = api
        self.task_id = task_id

    def handle_media_metrics(self, metrics: List[Metric]) -> List[Dict[str, Any]]:
        """
        处理媒体类型指标
        
        Args:
            metrics: 媒体指标列表
            
        Returns:
            API指标数据列表
        """
        seetrainlog.info(f"检测到 {len(metrics)} 个媒体类型指标，开始处理")
        api_metrics = []

        for metric in metrics:
            try:
                object_url = self._upload_single_media_file(metric)
                if object_url:
                    # 创建API指标
                    metric_datetime = datetime.fromtimestamp(metric.timestamp)
                    if isinstance(metric.value, Image):
                        mtype = MetricType.IMAGE
                    elif isinstance(metric.value, Audio):
                        mtype = MetricType.AUDIO
                    elif isinstance(metric.value, Video):
                        mtype = MetricType.VIDEO
                    else:
                        mtype = MetricType.TEXT  # fallback
                    api_metric = APIMetric(
                        task_id=self.task_id,
                        name=metric.name,
                        mtype=mtype,
                        step=metric.step,
                        text=object_url,
                        timestamp=metric_datetime
                    )
                    api_metrics.append(api_metric.model_dump(mode='json'))
                else:
                    seetrainlog.warning(f"媒体指标 {metric.name} 处理失败")
            except Exception as e:
                seetrainlog.error(f"处理媒体指标 {metric.name} 时发生错误: {e}")

        return api_metrics

    def _upload_single_media_file(self, metric: Metric) -> Optional[str]:
        """上传单个媒体文件"""
        if isinstance(metric.value, Image):
            return self._upload_image_file(metric)
        elif isinstance(metric.value, Audio):
            return self._upload_audio_file(metric)
        elif isinstance(metric.value, Video):
            return self._upload_video_file(metric)
        else:
            seetrainlog.warning(f"媒体指标 {metric.name} 的值不是支持的媒体类型，跳过上传: {type(metric.value)}")
            return None

    def _upload_image_file(self, metric: Metric) -> Optional[str]:
        """上传图片文件"""
        try:
            byte_data = metric.value.to_bytes()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{metric.name}_{timestamp}.jpg"
            file_type = FileTypeMapping.get_mime_type(metric.name)

            seetrainlog.debug(f"上传媒体文件: {filename}, 类型: {file_type}, 大小: {len(byte_data)} bytes")

            object_url = self.api.upload_file_data(
                file_data=byte_data,
                filename=filename,
                file_type=file_type,
                task_id=self.task_id
            )
            seetrainlog.info(f"媒体文件上传成功: {filename}, 响应: {object_url}")
            return object_url
        except Exception as e:
            seetrainlog.error(f"上传图片文件失败: {e}")
            return None

    def _upload_video_file(self, metric: Metric) -> Optional[str]:
        """上传视频文件"""
        try:
            seetrainlog.info(f"开始处理视频文件: {metric.name}, 帧数: {metric.value.get_frame_count()}")
            byte_data = metric.value.to_bytes()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{metric.name}_{timestamp}.mp4"
            file_type = 'video/mp4'

            seetrainlog.info(f"视频编码完成，开始上传: {filename}, 类型: {file_type}, 大小: {len(byte_data)} bytes")

            object_url = self.api.upload_file_data(
                file_data=byte_data,
                filename=filename,
                file_type=file_type,
                task_id=self.task_id
            )
            seetrainlog.info(f"视频文件上传成功: {filename}, 响应: {object_url}")
            return object_url
        except Exception as e:
            seetrainlog.error(f"上传视频文件失败: {e}")
            return None

    def _upload_audio_file(self, metric: Metric) -> Optional[str]:
        """上传音频文件"""
        try:
            byte_data = metric.value.to_bytes()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{metric.name}_{timestamp}.wav"
            file_type = 'audio/wav'

            seetrainlog.debug(f"上传媒体文件: {filename}, 类型: {file_type}, 大小: {len(byte_data)} bytes")

            object_url = self.api.upload_file_data(
                file_data=byte_data,
                filename=filename,
                file_type=file_type,
                task_id=self.task_id
            )
            seetrainlog.info(f"媒体文件上传成功: {filename}, 响应: {object_url}")
            return object_url
        except Exception as e:
            seetrainlog.error(f"上传音频文件失败: {e}")
            return None
