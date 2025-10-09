from enum import Enum, auto
from typing import List
from decimal import Decimal

class LogLevel(Enum):
    """日志级别"""

    Trace = auto()
    """链路"""
    Debug = auto()
    """调试"""
    Info = auto()
    """信息"""
    Warn = auto()
    """警告"""
    Error = auto()
    """错误"""
    @staticmethod
    def members() -> List[LogLevel]: ...

class Mode(Enum):
    """模式"""

    Backtest = auto()
    """回测"""
    Sandbox = auto()
    """沙盒"""
    Mainnet = auto()
    """主网"""
    @staticmethod
    def members() -> List[Mode]: ...

class Market(Enum):
    """市场"""

    Spot = auto()
    """现货"""
    Swap = auto()
    """合约"""
    @staticmethod
    def members() -> List[Market]: ...

class Direction(Enum):
    """交易方向"""

    Long = auto()
    """做多"""
    Short = auto()
    """做空"""
    @staticmethod
    def members() -> List[Direction]: ...

class Side(Enum):
    """买卖方向"""

    Buy = auto()
    """买入"""
    Sell = auto()
    """卖出"""
    @staticmethod
    def members() -> List[Side]: ...

class OrderStatus(Enum):
    """订单状态"""

    New = auto()
    """新创建"""
    Pending = auto()
    """待成交"""
    Complete = auto()
    """已完成"""
    Cancel = auto()
    """已取消"""
    @staticmethod
    def members() -> List[OrderStatus]: ...

class Interval(Enum):
    """周期"""

    Min = auto()
    """1分钟"""
    Min3 = auto()
    """3分钟"""
    Min5 = auto()
    """5分钟"""
    Min15 = auto()
    """15分钟"""
    Min30 = auto()
    """30分钟"""
    Hour = auto()
    """1小时"""
    Hour2 = auto()
    """2小时"""
    Hour4 = auto()
    """4小时"""
    Hour8 = auto()
    """8小时"""
    Hour12 = auto()
    """12小时"""
    Day = auto()
    """1天"""
    Day3 = auto()
    """3天"""
    Week = auto()
    """1周"""
    Month = auto()
    """1月"""
    @staticmethod
    def members() -> List[Interval]: ...

class Timer(Enum):
    """定时器"""

    Daily = auto()
    """每天"""
    Hourly = auto()
    """每小时"""
    Minutely = auto()
    """每分钟"""
    @staticmethod
    def members() -> List[Timer]: ...

class Volume:
    """数量"""

    total: Decimal
    """总数量"""
    avail: Decimal
    """可用数量"""
    frozen: Decimal
    """冻结数量"""
