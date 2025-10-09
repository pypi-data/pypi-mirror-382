from typing import TypedDict, Optional, Tuple
YRange = Optional[Tuple[Optional[float], Optional[float]]]

class LogContent(TypedDict):
    """日志内容字典类型

    结构示例:
    {
        "message": "hello world",
        "create_time": "2025-05-15 18:35:00",
        "epoch": 1
    }
    """

    message: str
    create_time: str
    epoch: int


class ColumnConfig:
    """
    列信息配置
    """

    def __init__(
        self,
        y_range: YRange = None,
        chart_name: Optional[str] = None,
        chart_index: Optional[str] = None,
        metric_name: Optional[str] = None,
        metric_color: Optional[Tuple[str, str]] = None,
    ):
        """
        生成的列信息配置对象
        :param y_range: y轴范围
        :param chart_name: 图表名称
        :param chart_index: 图表索引
        :param metric_name: 指标名称
        :param metric_color: 指标颜色
        """
        self.y_range: YRange = y_range
        self.chart_name: Optional[str] = chart_name
        self.chart_index: Optional[str] = chart_index
        self.metric_name: Optional[str] = metric_name
        self.metric_color: Optional[Tuple[str, str]] = metric_color

    def clone(
        self,
        y_range: YRange = None,
        chart_name: Optional[str] = None,
        chart_index: Optional[str] = None,
        metric_name: Optional[str] = None,
        metric_color: Optional[Tuple[str, str]] = None,
    ):
        """
        克隆一个新的ColumnConfig对象，并且可以修改其中的参数
        :param y_range: y轴范围
        :param chart_name: 图表名称
        :param chart_index: 图表索引
        :param metric_name: 指标名称
        :param metric_color: 指标颜色
        :return: 新的ColumnConfig对象
        """
        return ColumnConfig(
            y_range=y_range if y_range is not None else self.y_range,
            chart_name=chart_name if chart_name is not None else self.chart_name,
            metric_name=metric_name if metric_name is not None else self.metric_name,
            chart_index=chart_index if chart_index is not None else self.chart_index,
            metric_color=metric_color if metric_color is not None else self.metric_color,
        )