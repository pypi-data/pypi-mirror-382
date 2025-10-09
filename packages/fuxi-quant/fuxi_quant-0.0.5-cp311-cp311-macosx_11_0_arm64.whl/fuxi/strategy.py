from abc import ABC
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, Optional, Tuple
from .__core import (
    Context,
    Codes,
    Mode,
    Volume,
    Symbol,
    LogLevel,
    Backtest,
    Timer,
    Order,
    Direction,
    Side,
    DirectionPosition,
)
import polars as pl
from polars import DataFrame
from datetime import datetime


class Strategy(ABC):
    # ================================================================ #
    # 属性
    # ================================================================ #

    @property
    def mode(self) -> Mode:
        """模式"""
        return self.__context__.mode

    @property
    def time(self) -> datetime:
        """当前时间"""
        return self.__context__.time

    @property
    def cash(self) -> Volume:
        """现货资金"""
        return self.__context__.cash

    @property
    def margin(self) -> Volume:
        """合约保证金"""
        return self.__context__.margin

    @property
    def pnl(self) -> Decimal:
        """未实现盈亏"""
        return self.__context__.pnl

    @property
    def symbols(self) -> Dict[Codes, Symbol]:
        """交易对"""
        return self.__context__.symbols

    @property
    def history_size(self) -> int:
        """历史数据大小"""
        return self.__context__.history_size

    # ================================================================ #
    # 日志API
    # ================================================================ #

    def trace_log(self, *args):
        """显示链路日志"""
        self.__context__.show_log(LogLevel.Trace, *args)

    def debug_log(self, *args):
        """显示调试日志"""
        self.__context__.show_log(LogLevel.Debug, *args)

    def info_log(self, *args):
        """显示信息日志"""
        self.__context__.show_log(LogLevel.Info, *args)

    def warn_log(self, *args):
        """显示警告日志"""
        self.__context__.show_log(LogLevel.Warn, *args)

    def error_log(self, *args):
        """显示错误日志"""
        self.__context__.show_log(LogLevel.Error, *args)

    # ================================================================ #
    # 辅助API
    # ================================================================ #

    @staticmethod
    def millis_to_time(millis: int) -> datetime:
        """毫秒转换为时间"""
        return Context.millis_to_time(millis)

    @staticmethod
    def nanos_to_time(nanos: int) -> datetime:
        """纳秒转换为时间"""
        return Context.nanos_to_time(nanos)

    @staticmethod
    def str_to_time(s: str) -> datetime:
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
        return Context.str_to_time(s)

    @staticmethod
    def time_to_str(t: datetime, fmt: str) -> str:
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
        return Context.time_to_str(t, fmt)

    @staticmethod
    def new_id() -> str:
        """生成唯一id"""
        return Context.new_id()

    def flush_signal(self, signal: DataFrame, name: str = "default"):
        """
        刷新信号
        - [`signal`]: 信号
        - [`name`]: 信号名
        """
        self.__signals__[name] = signal.rechunk()

    def get_signal(self, name: str = "default") -> DataFrame | None:
        """
        获取信号
        - [`name`]: 信号名
        """
        if name not in self.__signals__:
            return None
        if self.mode == Mode.Backtest:
            return self.__signals__[name].slice(0, self.__backtest__.offset).tail(self.history_size)
        else:
            return self.__signals__[name]

    def get_candle(self, code: Codes) -> DataFrame | None:
        """
        获取K线
        - [`code`]: 交易对
        """
        if code not in self.__candles__:
            return None
        if self.mode == Mode.Backtest:
            return self.__candles__[code].slice(0, self.__backtest__.offset).tail(self.history_size)
        else:
            return self.__candles__[code]

    def safe_size(self, code: Codes, val: Decimal) -> Decimal:
        """
        安全转换为Size
        - [`code`]: 交易对
        - [`val`]: 值
        """
        scale = Decimal('0.' + '0' * code.decimals())
        return val.quantize(scale, rounding=ROUND_DOWN)

    # ================================================================ #
    # 订单API
    # ================================================================ #

    def buy(
        self,
        code: Codes,
        size: Decimal,
        price: Decimal,
        id: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> Tuple[bool, Optional[Order], Optional[str]]:
        """
        做多开仓

        参数
        - [`code`]: 交易对
        - [`size`]: 数量
        - [`price`]: 价格
        - [`id`]: 订单id
        - [`remark`]: 备注

        结果
        `[0]`: 是否成功
        `[1]`: 订单
        `[2]`: 错误信息
        """
        return self.__context__.place_order(
            code,
            Direction.Long,
            Side.Buy,
            size,
            price,
            id,
            remark,
        )

    def sell(
        self,
        code: Codes,
        size: Decimal,
        price: Decimal,
        id: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> Tuple[bool, Optional[Order], Optional[str]]:
        """
        做多平仓

        参数
        - [`code`]: 交易对
        - [`size`]: 数量
        - [`price`]: 价格
        - [`id`]: 订单id
        - [`remark`]: 备注

        结果
        `[0]`: 是否成功
        `[1]`: 订单
        `[2]`: 错误信息
        """
        return self.__context__.place_order(
            code,
            Direction.Long,
            Side.Sell,
            size,
            price,
            id,
            remark,
        )

    def short(
        self,
        code: Codes,
        size: Decimal,
        price: Decimal,
        id: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> Tuple[bool, Optional[Order], Optional[str]]:
        """
        做空开仓

        参数
        - [`code`]: 交易对
        - [`size`]: 数量
        - [`price`]: 价格
        - [`id`]: 订单id
        - [`remark`]: 备注

        结果
        `[0]`: 是否成功
        `[1]`: 订单
        `[2]`: 错误信息
        """
        return self.__context__.place_order(
            code,
            Direction.Short,
            Side.Sell,
            size,
            price,
            id,
            remark,
        )

    def cover(
        self,
        code: Codes,
        size: Decimal,
        price: Decimal,
        id: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> Tuple[bool, Optional[Order], Optional[str]]:
        """
        做空平仓

        参数
        - [`code`]: 交易对
        - [`size`]: 数量
        - [`price`]: 价格
        - [`id`]: 订单id
        - [`remark`]: 备注

        结果
        `[0]`: 是否成功
        `[1]`: 订单
        `[2]`: 错误信息
        """
        return self.__context__.place_order(
            code,
            Direction.Short,
            Side.Buy,
            size,
            price,
            id,
            remark,
        )

    def send_order(
        self,
        code: Codes,
        direction: Direction,
        side: Side,
        size: Decimal,
        price: Decimal,
        id: Optional[str] = None,
        remark: Optional[str] = None,
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
        return self.__context__.place_order(
            code,
            direction,
            side,
            size,
            price,
            id,
            remark,
        )

    def cancel(self, code: Codes, id: str) -> Tuple[bool, Optional[str]]:
        """
        取消订单

        参数
        - [`code`]: 交易对
        - [`id`]: 订单id

        结果
        `[0]`: 是否成功
        `[1]`: 错误信息
        """
        self.__context__.cancel_order(code, id)

    # ================================================================ #
    # 事件
    # ================================================================ #
    def on_init(self, params: Dict[str, Any]):
        """初始化事件"""

    def on_stop(self):
        """停止事件"""

    def on_candle(self, code: Codes, candle: DataFrame):
        """K线事件"""

    def on_signal(self):
        """信号事件"""

    def on_timer(self, timer: Timer):
        """定时器事件"""

    def on_position(self, position: DirectionPosition):
        """持仓事件"""

    def on_order(self, order: Order):
        """订单事件"""

    def on_cash(self):
        """资金事件"""

    def on_margin(self):
        """保证金事件"""

    # ================================================================ #
    # 内部
    # ================================================================ #

    __context__: Context
    __backtest__: Backtest
    __candles__: Dict[Codes, DataFrame] = {}
    __signals__: Dict[str, DataFrame] = {}

    def __on_inject_context__(self, context: Context):
        self.__context__ = context

    def __on_inject_backtest__(self, backtest: Backtest):
        self.__backtest__ = backtest

    def __on_init__(self, params: Dict[str, Any]):
        self.on_init(params)

    def __on_stop__(self):
        self.on_stop()

    def __on_history_candle__(self, code: Codes, candles):
        df: DataFrame = pl.from_arrow(candles).rechunk()
        self.__candles__[code] = df
        self.on_candle(code, df)
        if self.mode != Mode.Backtest:
            self.on_signal()

    def __on_candle__(self, code: Codes, candles):
        candles: DataFrame = pl.from_arrow(candles)
        df = (
            pl.concat(
                [self.__candles__[code], candles],
                how="horizontal",
            )
            .unique(
                subset=["time"],
                keep="last",
                maintain_order=True,
            )
            .tail(self.history_size)
            .rechunk()
        )
        self.__candles__[code] = df
        self.on_candle(code, df)
        self.on_signal()

    def __on_backtest_tick__(self):
        self.on_signal()

    def __on_timer__(self, timer: Timer):
        self.on_timer(timer)

    def __on_position__(self, position: DirectionPosition):
        self.on_position(position)

    def __on_order__(self, order: Order):
        self.on_order(order)

    def __on_cash__(self):
        self.on_cash()

    def __on_margin__(self):
        self.on_margin()
