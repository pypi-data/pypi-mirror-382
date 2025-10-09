"""
@author: cunyue
@file: __init__.py.py
@time: 2024/12/3 20:14
@description: 硬件信息采集
"""

from typing import Callable, List, Any, Optional, Tuple

from .cpu import get_cpu_info
from .disk import get_disk_info
from .gpu.metax import get_metax_gpu_info
from .gpu.moorethreads import get_moorethreads_gpu_info
from .gpu.nvidia import get_nvidia_gpu_info
from .memory import get_memory_size
from .network import get_network_info   
from .soc.apple import get_apple_chip_info
from .type import HardwareFuncResult, HardwareCollector, HardwareInfo
from .utils import is_system_key

__all__ = ["get_hardware_info", "HardwareCollector", "HardwareInfo", "is_system_key"]


def get_hardware_info() -> Tuple[Optional[Any], List[HardwareCollector]]:
    """
    采集硬件信息，包括CPU、GPU、内存、硬盘等
    """
    monitor_funcs = []
    # 我们希望计算芯片的信息放在最前面，前端展示用
    nvidia = dec_hardware_func(get_nvidia_gpu_info, monitor_funcs)
    moorethreads = dec_hardware_func(get_moorethreads_gpu_info, monitor_funcs)
    apple = dec_hardware_func(get_apple_chip_info, monitor_funcs)
    metax = dec_hardware_func(get_metax_gpu_info, monitor_funcs)
    c = dec_hardware_func(get_cpu_info, monitor_funcs)
    m = dec_hardware_func(get_memory_size, monitor_funcs)
    d = dec_hardware_func(get_disk_info, monitor_funcs)
    n = dec_hardware_func(get_network_info, monitor_funcs)

    info = {
        "memory": None,
        "cpu": None,
        "disk": None,
        "network": None,
        "gpu": None,
        "soc": None,
    }
    
    # Convert CPU info to HardwareInfo format
    if c is not None:
        cpu_name = c.get("brand", "Unknown CPU")
        if c.get("cores"):
            cpu_name += f" ({c['cores']} cores)"
        info["cpu"] = {
            "key": "cpu",
            "value": cpu_name,
            "name": "CPU"
        }
    
    # Convert Memory info to HardwareInfo format
    if m is not None:
        info["memory"] = {
            "key": "memory",
            "value": f"{m} GB",
            "name": "Memory"
        }
    
    # Convert Disk info to HardwareInfo format
    if d is not None:
        info["disk"] = {
            "key": "disk",
            "value": "Available",
            "name": "Disk"
        }
    
    # Convert Network info to HardwareInfo format
    if n is not None:
        info["network"] = {
            "key": "network",
            "value": "Available",
            "name": "Network"
        }
    
    # Convert GPU info to HardwareInfo format
    if nvidia is not None:
        info["gpu"] = {
            "key": "nvidia",
            "value": nvidia.get("name", "NVIDIA GPU"),
            "name": "NVIDIA GPU"
        }
    elif moorethreads is not None:
        info["gpu"] = {
            "key": "moorethreads", 
            "value": moorethreads.get("name", "MooreThreads GPU"),
            "name": "MooreThreads GPU"
        }
    elif metax is not None:
        info["gpu"] = {
            "key": "metax",
            "value": metax.get("name", "Metax GPU"), 
            "name": "Metax GPU"
        }
    
    # Convert SOC info to HardwareInfo format
    if apple is not None:
        info["soc"] = {
            "key": "apple",
            "value": apple.get("type", "Apple Chip"),
            "name": "Apple SOC"
        }
    
    return filter_none(info, fallback={}), monitor_funcs


def dec_hardware_func(
    func: Callable[[], HardwareFuncResult],
    monitor_funcs: List[HardwareCollector],
) -> Optional[Any]:
    """
    装饰器，用于记录硬件信息采集函数
    """
    x, y = func()
    if y:
        monitor_funcs.append(y)
    return x


def filter_none(data, fallback=None):
    """
    过滤掉字典中值为None的键值对，只对字典有效
    """
    if isinstance(data, dict):
        data = {k: v for k, v in data.items() if v is not None and v != {}}  # 过滤掉空字典
        if all(v is None for v in data.values()):
            return fallback
    return data
