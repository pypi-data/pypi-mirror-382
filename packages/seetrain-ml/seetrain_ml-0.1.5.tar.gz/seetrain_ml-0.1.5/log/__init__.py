#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from rich.console import Console
from .log import SeeTrainLog

# 创建默认的日志实例，只输出到文件
log_file = os.path.join(os.getcwd(), "seetrain.log")
seetrainlog: SeeTrainLog = SeeTrainLog("seetrain", console_output=False)
# 设置文件输出
seetrainlog.console = Console(file=open(log_file, "a", encoding="utf-8"))
start_proxy = seetrainlog.start_proxy
reset = seetrainlog.reset

def create_file_only_logger(name: str, log_file_path: str = None):
    """
    创建一个只输出到文件的日志实例
    :param name: 日志名称
    :param log_file_path: 日志文件路径，如果为None则使用默认路径
    :return: SeeTrainLog实例
    """
    if log_file_path is None:
        log_file_path = os.path.join(os.getcwd(), f"{name}.log")
    
    logger = SeeTrainLog(name, console_output=False)
    logger.console = Console(file=open(log_file_path, "a", encoding="utf-8"))
    return logger

__all__ = ["seetrainlog", "start_proxy", "reset", "create_file_only_logger"]
