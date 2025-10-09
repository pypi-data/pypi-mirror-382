from typing import Any, List, Tuple
from .code import Codes
from .base import LogLevel
from datetime import datetime
from decimal import Decimal

class Backtest:
    """回测引擎"""

    begin: datetime
    """开始时间"""
    end: datetime
    """结束时间"""
    offset: int
    """数据偏移量"""

    def __init__(
        self,
        strategy: Any,
        params: Any,
        begin: str,
        end: str,
        symbols: List[Tuple[Codes, Decimal, Decimal, Decimal]],
        cash: Decimal = 1000,
        margin: Decimal = 1000,
        history_size: int = 5000,
        log_level: Tuple[LogLevel, LogLevel] = (LogLevel.Info, LogLevel.Info),
    ):
        """
        初始化回测引擎
        - [`strategy`]: 策略类
        - [`params`]: 策略参数
        - [`begin`]: 开始时间
        - [`end`]: 结束时间
        - [`symbols`]: 交易对配置
        - [`symbols.item`]: (交易对, 吃单费率, 挂单费率, 杠杆倍数)
        - [`cash`]: 现货资金
        - [`margin`]: 合约保证金
        - [`history_size`]: 历史数据大小
        - [`log_level`]: 日志级别
        - [`log_level.0`]: 引擎日志级别
        - [`log_level.1`]: 策略日志级别
        """

    def launche(self):
        """启动回测"""
