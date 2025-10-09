#!/usr/bin/env python
# # -*- coding: utf-8 -*-

import os
import platform
from pathlib import Path

try:
    from typing import Annotated, Literal, Optional  # Python 3.9+
except ImportError:
    from typing_extensions import Annotated, Literal, Optional  # Python 3.8

from pydantic import BaseModel, StrictBool, DirectoryPath, Field, PositiveInt


def is_windows():
    return platform.system() == "Windows"


class Settings(BaseModel):
    # ---------------------------------- 硬件监控部分 ----------------------------------
    # 是否开启硬件监控，如果元信息的相关采集被关闭，则此项无效
    hardware_monitor: StrictBool = True
    # 磁盘IO监控的路径
    disk_io_dir: DirectoryPath = Field(
        default_factory=lambda: str(Path(os.environ.get("SystemDrive", "C:")).resolve() if is_windows() else Path("/"))
    )
    hardware_interval: Optional[PositiveInt] = Field(
        default=None,
        ge=5,
        description="Hardware monitoring collection interval, in seconds, minimum value is 5 seconds.",
    )


settings = Settings()


def get_settings():
    """获取当前全局设置"""
    global settings
    return settings


def set_settings(new_settings: Settings) -> Settings:
    global settings
    settings = new_settings
    return settings


def reset_settings():
    global settings
    settings = Settings()
