import platform
import os
from .hardware import *
from .conda import *
from .requirements import *
from .python import *

def get_host_name():
    return platform.node()

def get_os():
    return platform.system()

def get_pid():
    return os.getpid()


__all__ = ["get_hardware_info", "get_conda_info", "get_requirements", "get_python_info", "get_python_identifier", "get_python_version", "get_python_detail", "get_python_interpreter", "get_python_workdir", "get_python_cmd", "get_python_libraries", "get_host_name", "get_os", "get_pid"]