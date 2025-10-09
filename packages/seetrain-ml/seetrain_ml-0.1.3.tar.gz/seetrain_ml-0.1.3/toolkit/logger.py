from typing import Literal, Union
from datetime import datetime

from rich.console import Console
from rich.text import Text

Levels = Union[Literal["debug", "info", "warning", "error", "critical"], str]


class SeeTrainLogger:

    def __init__(self, name=__name__.lower(), level: Levels = "info", file=None, console_output=True):
        self.console = Console(file=file)
        self.__console_output = console_output
        self.__level: int = 0
        self.__name = name
        self.__config = {
            "debug": (10, 'dim cyan bold', 'dim white'),      # 青色标签，白色消息
            "info": (20, 'bright_blue bold', 'white'),        # 亮蓝色标签，白色消息
            "warning": (30, 'bright_yellow bold', 'yellow'),  # 亮黄色标签，黄色消息
            "error": (40, 'bright_red bold', 'red'),          # 亮红色标签，红色消息
            "critical": (50, 'bright_red on red bold', 'bright_red'), # 红底亮红字标签，亮红色消息
        }
        self.__can_log = True

        self.level = level

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level: Levels):
        """
        设置日志等级
        :param level: 日志等级，可选值为 debug, info, warning, error, critical，如果传入的值不在可选值中，则默认为 info
        """
        if level not in ("debug", "info", "warning", "error", "critical"):
            _level = 20  # info
        else:
            _level = self.__config[level][0]
        self.__level = _level

    def disable_log(self):
        """
        关闭日志输出，实例化时默认开启
        """
        self.__can_log = False

    def enable_log(self):
        """
        开启日志输出
        """
        self.__can_log = True

    def set_console_output(self, console_output: bool):
        """
        设置是否输出到控制台
        :param console_output: True表示输出到控制台，False表示只输出到文件
        """
        self.__console_output = console_output

    def __print(self, log_level: str, *args, **kwargs):
        """
        打印日志
        """
        if not self.__can_log:
            return
        level, label_style, message_style = self.__config[log_level]
        if level < self.__level:
            return
        
        # 生成包含时间的前缀
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = Text(f"[{current_time}] ", style='dim') + \
                Text(self.__name, style=label_style, no_wrap=True) + \
                Text(':', style="default")
        
        if kwargs.get("sep") == '':
            prefix += " "
        
        # 如果设置了不输出到控制台，则只输出到文件（如果file参数不为None）
        if not self.__console_output and self.console.file is None:
            return
        
        # 为消息内容应用颜色
        colored_args = []
        for arg in args:
            if isinstance(arg, str):
                colored_args.append(Text(arg, style=message_style))
            else:
                colored_args.append(arg)
        
        self.console.print(prefix, *colored_args, **kwargs)

    # 发送调试消息
    def debug(self, *args, **kwargs):
        return self.__print("debug", *args, **kwargs)

    # 发送通知
    def info(self, *args, **kwargs):
        return self.__print("info", *args, **kwargs)

    # 发生警告
    def warning(self, *args, **kwargs):
        return self.__print("warning", *args, **kwargs)

    # 发生错误
    def error(self, *args, **kwargs):
        return self.__print("error", *args, **kwargs)

    # 致命错误
    def critical(self, *args, **kwargs):
        return self.__print("critical", *args, **kwargs)
