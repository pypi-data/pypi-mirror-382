#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from typing_extensions import TypedDict
from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(
        # 确保datetime正确序列化为ISO格式字符串
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    def __getitem__(self, key):
        return getattr(self, key)


# ==================== Metrics 相关数据结构 ====================
class Metric(BaseModel):
    """指标数据结构"""
    task_id: str  # 任务ID
    name: str  # 指标名称
    mtype: str  # 指标类型: number, text, image, audio, video, chart, csv
    step: Optional[int] = None  # 训练步数
    number: Optional[float] = None  # 数值类型指标的值
    text: Optional[str] = None  # 文本类型指标的值
    json_data: Optional[Dict[str, Any]] = None  # JSON类型指标的值
    timestamp: datetime  # 时间戳


# ==================== Summary 相关数据结构 ====================
class ConfigItem(BaseModel):
    """配置项"""
    key: str  # 配置键
    value: Any  # 配置值


class MetricsItem(BaseModel):
    """指标项"""
    key: str  # 指标键
    mtype: str  # 指标类型
    group: str  # 指标分组
    value: Optional[Any] = None  # 指标值（可选）


# 定义硬件信息类型
class HardwareInfo(TypedDict):
    # 硬件信息键
    key: str
    # 硬件信息值
    value: Union[str, int, float]
    # 硬件信息名称
    name: str


class SystemInfo(BaseModel):
    """系统信息"""
    host_name: str  # 主机名
    os: str  # 操作系统
    cpu: Optional[HardwareInfo] = None  # CPU
    gpu: Optional[HardwareInfo] = None  # GPU
    soc: Optional[HardwareInfo] = None  # SOC
    disk: Optional[HardwareInfo] = None  # 磁盘
    memory: Optional[HardwareInfo] = None  # 内存
    network: Optional[HardwareInfo] = None  # 网络
    pid: str  # 进程ID


class PythonInfo(BaseModel):
    """Python环境信息"""
    python: str  # Python标识
    version: str  # 版本
    detail: str  # 详细信息
    interpreter: str  # Python解释器
    workdir: str  # 工作目录
    cmd: str  # 运行命令
    libraries: List[str]  # 依赖库列表


class Summary(BaseModel):
    """任务摘要"""
    task_id: str  # 任务ID
    project: str  # 项目名
    metrics: Dict[str, MetricsItem]  # 指标字典
    config: Optional[List[ConfigItem]] = None  # 配置项列表
    system: Optional[SystemInfo] = None  # 系统信息
    python: Optional[PythonInfo] = None  # Python环境信息
