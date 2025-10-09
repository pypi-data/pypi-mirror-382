#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from typing import Union, Dict, Any
from datetime import datetime

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from api import *
from env import Env
from .run import *
from .run.metadata import *
from .modules import DataType, Image, Audio, Video

from formatter import format_metrics_data
from log import seetrainlog

api = OpenAPI(Env.BaseURL.value)

# 全局指标存储
_global_metrics: Dict[str, MetricsItem] = {}
_global_metric_values: Dict[str, DataType] = {}  # 存储指标值用于比较

# 创建专门的指标日志记录器
_metrics_logger = logging.getLogger('seetrain.metrics')
_metrics_logger.setLevel(logging.INFO)

# 如果还没有处理器，添加一个控制台处理器
if not _metrics_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    _metrics_logger.addHandler(handler)
    _metrics_logger.propagate = False  # 防止传播到父日志记录器


def _detect_metric_type(value: Any) -> str:
    """检测指标值的类型"""
    if isinstance(value, (int, float)):
        return "number"
    elif isinstance(value, Image):
        return "image"
    elif isinstance(value, Audio):
        return "audio"
    elif isinstance(value, Video):
        return "video"
    elif isinstance(value, str):
        return "text"
    elif isinstance(value, (dict, list)):
        return "json"
    else:
        return "text"  # 默认类型


def _metrics_changed(new_metrics: Dict[str, DataType]) -> bool:
    """检查新指标是否与全局指标不同（只检查key是否发生变化）"""
    global _global_metric_values

    if len(new_metrics) != len(_global_metric_values):
        return True

    for key in new_metrics.keys():
        if key not in _global_metric_values:
            return True

    return False


def _update_global_metrics(new_metrics: Dict[str, DataType]):
    """更新全局指标"""
    global _global_metric_values

    for key, value in new_metrics.items():
        mtype = _detect_metric_type(value)
        group = "default"
        if "/" in key:
            group = key.split("/")[0]
        _global_metrics[key] = MetricsItem(
            key=key,
            mtype=mtype,
            group=group
        )
        if mtype == "image" or mtype == "audio" or mtype == "video":
            value = value.to_bytes()
        if mtype == "text":
            value = value.get_data()
        # 同时更新值存储
        _global_metric_values[key] = value


def init(
        config: Union[dict, str] = None,
):
    # 获取系统硬件信息
    hardwareInfo, _ = get_hardware_info()

    system_info = SystemInfo(
        host_name=get_host_name(),
        os=get_os(),
        pid=str(get_pid()),
        cpu=hardwareInfo.get("cpu"),
        gpu=hardwareInfo.get("gpu"),
        soc=hardwareInfo.get("soc"),
        disk=hardwareInfo.get("disk"),
        memory=hardwareInfo.get("memory"),
        network=hardwareInfo.get("network"),
    )
    # 创建默认的配置和指标
    config_list = []
    if config:
        if isinstance(config, dict):
            for key, value in config.items():
                config_list.append({"key": key, "value": value})
        else:
            config_list.append({"key": "config", "value": config})

    # 创建默认的指标
    metrics_dict = {}

    # 创建默认的Python信息
    python_info = PythonInfo(
        python=get_python_identifier(),
        version=get_python_version(),
        detail=get_python_detail(),
        interpreter=get_python_interpreter(),
        workdir=get_python_workdir(),
        cmd=get_python_cmd(),
        libraries=get_python_libraries(),
    )

    try:
        api.upsert_summary(
            task_id=Env.TaskID.value,
            project=Env.Project.value,
            metrics=metrics_dict,
            config=config_list,
            system=system_info,
            python=python_info
        )
        _metrics_logger.info("seetrain: 👏 Init success")
        _metrics_logger.info(f"seetrain: 🙋🏻 Run data will be saved locally in {python_info.workdir}/seetrain.log ")
    except Exception as e:
        _metrics_logger.error(f"seetrain: ❌ Init failed, but training can continue: {e}")

    # 启动指标消费线程
    try:
        from sync.metrics import start_consumer
        start_consumer()
        seetrainlog.info("指标消费线程已启动")
    except Exception as e:
        seetrainlog.error(f"seetrain: metrics consumer start failed: {e}")
    _metrics_logger.info(f"seetrain: 🚀 View run at {Env.ViewURL.value}?task_id={Env.TaskID.value}")
    _metrics_logger.info("")


def log(
        data: Dict[str, DataType],
        epoch: int = None,
        step: int = None,
        print_to_console: bool = True
):
    """
    记录训练指标数据
    
    Args:
        data: 指标数据字典
        step: 训练步数（必填）
        print_to_console: 是否打印到控制台
    """
    global _global_metrics

    # 检查指标是否发生变化
    if _metrics_changed(data):
        # 更新全局指标
        _update_global_metrics(data)

        try:
            # 增量更新摘要信息
            api.upsert_summary(
                task_id=Env.TaskID.value,
                project=Env.Project.value,
                metrics=_global_metrics,
            )
            if print_to_console:
                log_data = ""
                if epoch is not None:
                    log_data += f' epoch: {epoch}'
                if step is not None:
                    log_data += f' step: {step}'
                seetrainlog.info(f"指标已更新 ({log_data}): {data}")
        except Exception as e:
            seetrainlog.error(f"更新指标失败: {e}")

    # 手动同步指标到队列
    try:
        from sync.metrics import get_queue
        queue = get_queue()
        queue.add_metrics_dict(data, step=step)
    except Exception as e:
        seetrainlog.error(f"同步指标到队列失败: {e}")

    # 记录指标数据
    if print_to_console:
        # 格式化并打印指标数据
        formatted_metrics = format_metrics_data(data, step, epoch)
        # 使用专门的指标日志记录器
        _metrics_logger.info(formatted_metrics)


def finish():
    """完成训练，停止指标消费线程"""
    try:
        seetrainlog.info("指标消费线程已停止")
    except Exception as e:
        seetrainlog.error(f"停止指标消费线程失败: {e}")
