#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import platform
import subprocess
import pkg_resources
from typing import TypedDict, List

class PythonFuncResult(TypedDict):
    python: str
    version: str
    detail: str
    interpreter: str
    workdir: str
    cmd: str
    libraries: List[str]

def get_python_info() -> PythonFuncResult:
    """获取Python环境信息"""
    return {
        "python": get_python_identifier(),
        "version": get_python_version(),
        "detail": get_python_detail(),
        "interpreter": get_python_interpreter(),
        "workdir": get_python_workdir(),
        "cmd": get_python_cmd(),
        "libraries": get_python_libraries(),
    }

def get_python_identifier() -> str:
    """获取Python标识符"""
    return f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def get_python_version() -> str:
    """获取Python版本"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def get_python_detail() -> str:
    """获取Python详细信息"""
    return f"{platform.python_implementation()} {sys.version}"

def get_python_interpreter() -> str:
    """获取Python解释器路径"""
    return sys.executable

def get_python_workdir() -> str:
    """获取当前工作目录"""
    return os.getcwd()

def get_python_cmd() -> str:
    """获取Python命令行参数"""
    return " ".join(sys.argv)

def get_python_libraries() -> List[str]:
    """获取已安装的Python库列表"""
    try:
        # 获取已安装的包
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        # 过滤掉一些系统包，只保留主要的第三方库
        filtered_packages = []
        for package in installed_packages:
            # 跳过一些常见的系统包
            if package.lower() not in ['pip', 'setuptools', 'wheel', 'pkg-resources']:
                try:
                    # 获取版本信息
                    version = pkg_resources.get_distribution(package).version
                    filtered_packages.append(f"{package}=={version}")
                except:
                    filtered_packages.append(package)
        return sorted(filtered_packages)
    except Exception:
        # 如果获取失败，返回空列表
        return []

