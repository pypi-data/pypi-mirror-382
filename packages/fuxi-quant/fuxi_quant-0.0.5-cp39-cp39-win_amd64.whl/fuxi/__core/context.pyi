from typing import Dict, Optional, Tuple
from .market import Symbol
from .code import Codes
from .base import LogLevel, Mode, Volume, Direction, Side
from .order import Order
from datetime import datetime
from decimal import Decimal

class Context:
    """上下文"""

    mode: Mode
    """模式"""
    time: datetime
    """当前时间"""
    cash: Volume
    """现货资金"""
    margin: Volume
    """合约保证金"""
    pnl: Decimal
    """未实现盈亏"""
    symbols: Dict[Codes, Symbol]
    """交易对"""
    history_size: int
    """历史数据大小"""
    def show_log(self, level: LogLevel, *args):
        """显示日志"""

    def place_order(
        self,
        code: Codes,
        direction: Direction,
        side: Side,
        size: Decimal,
        price: Decimal,
        id: Optional[str],
        remark: Optional[str],
    ) -> Tuple[bool, Optional[Order], Optional[str]]:
        """
        下单

        参数
        - [`code`]: 交易对
        - [`direction`]: 交易方向
        - [`side`]: 买卖方向
        - [`size`]: 订单数量
        - [`price`]: 订单价格
        - [`id`]: 订单id
        - [`remark`]: 备注

        结果
        `[0]`: 是否成功
        `[1]`: 订单
        `[2]`: 错误信息
        """

    def cancel_order(self, code: Codes, id: str) -> Tuple[bool, Optional[str]]:
        """
        取消订单

        参数
        - [`code`]: 交易对
        - [`id`]: 订单id

        结果
        `[0]`: 是否成功
        `[1]`: 错误信息
        """

    @staticmethod
    def millis_to_time(millis: int) -> datetime:
        """毫秒转换为时间"""

    @staticmethod
    def nanos_to_time(nanos: int) -> datetime:
        """纳秒转换为时间"""

    @staticmethod
    def str_to_time(s: int) -> datetime:
        """
        字符串转换为时间

        格式如下:
        - 2020
        - 2020-01
        - 2020-01-02
        - 2020-01-02 03
        - 2020-01-02 03:04
        - 2020-01-02 03:04:05
        - 2020-01-02 03:04:05.678
        - 2020
        - 202001
        - 20200102
        - 2020010203
        - 202001020304
        - 20200102030405
        - 20200102030405678
        """

    @staticmethod
    def time_to_str(t: datetime, fmt: str) -> datetime:
        """
        时间转换为字符串
        [`fmt`]: 格式如下
        - %Y: 年
        - %m: 月
        - %d: 日
        - %H: 时
        - %M: 分
        - %S: 秒
        - %3f: 毫秒
        """

    @staticmethod
    def new_id() -> str:
        """生成唯一id"""
