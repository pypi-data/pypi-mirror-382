from abc import ABC
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, List, Optional, Tuple
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
import talib as ta
import numpy as np
from numpy.typing import NDArray


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

    def get_equity(self) -> Decimal:
        """获取权益"""
        return self.__context__.get_equity()

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
    __equity_curve__: List[Tuple[datetime, Decimal]] = []

    def __on_inject_context__(self, context: Context):
        self.__context__ = context

    def __on_inject_backtest__(self, backtest: Backtest):
        self.__backtest__ = backtest

    def __on_init__(self, params: Dict[str, Any]):
        self.on_init(params)

    def __on_stop__(self):
        self.on_stop()
        if self.mode == Mode.Backtest:
            self.print_metrics()

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
        if self.mode == Mode.Backtest and timer == Timer.Minutely:
            self.__equity_curve__.append((self.time, self.get_equity()))
        self.on_timer(timer)

    def __on_position__(self, position: DirectionPosition):
        self.on_position(position)

    def __on_order__(self, order: Order):
        self.on_order(order)

    def __on_cash__(self):
        self.on_cash()

    def __on_margin__(self):
        self.on_margin()

    # ================================================================ #
    # 绩效报告
    # ================================================================ #

    def metrics(self):
        if self.mode != Mode.Backtest:
            return None

        eq_times = [t for t, _ in self.__equity_curve__]
        eq_vals = [float(e) for _, e in self.__equity_curve__]

        df = pl.DataFrame(
            {
                "time": eq_times,
                "equity": eq_vals,
            }
        )
        lf = df.lazy()

        lf_day = (
            lf.sort("time")
            .with_columns(day=pl.col("time").dt.date())
            .group_by("day")
            .agg(equity=pl.col("equity").last())
            .sort("day")
        )

        lf_day_ret = lf_day.with_columns(ret=pl.col("equity") / pl.col("equity").shift(1) - 1.0).filter(
            pl.col("ret").is_finite()
        )

        span_days_df = lf_day.select(
            pl.col("day").min().alias("day_min"),
            pl.col("day").max().alias("day_max"),
            pl.col("equity").first().alias("eq_first"),
            pl.col("equity").last().alias("eq_last"),
        ).collect()
        if span_days_df.height == 0:
            return None
        day_min = span_days_df["day_min"].item()
        day_max = span_days_df["day_max"].item()
        eq_first = float(span_days_df["eq_first"].item())
        eq_last = float(span_days_df["eq_last"].item())

        days_span = (day_max - day_min).days if day_min is not None and day_max is not None else 0
        total_return = (eq_last / eq_first - 1.0) if eq_first > 0 else None
        annual_return = None
        if total_return is not None and days_span >= 1:
            annual_return = (1.0 + total_return) ** (365.0 / float(days_span)) - 1.0

        ret_stats = lf_day_ret.select(
            pl.col("ret").mean().alias("ret_mean"),
            pl.col("ret").std().alias("ret_std"),
        ).collect()
        if ret_stats.height == 0:
            return None
        mean_daily_return = ret_stats["ret_mean"].item()
        std_daily = ret_stats["ret_std"].item()

        downside_std_df = (
            lf_day_ret.with_columns(ret_down=pl.when(pl.col("ret") < 0.0).then(pl.col("ret")).otherwise(0.0))
            .select(pl.col("ret_down").std().alias("down_std"))
            .collect()
        )
        downside_std = downside_std_df["down_std"].item() if downside_std_df.height > 0 else None

        vol_annual = (std_daily * (365.0**0.5)) if std_daily is not None else None
        downside_vol_annual = (downside_std * (365.0**0.5)) if downside_std is not None else None

        lf_dd = (
            lf_day.with_columns(running_max=pl.col("equity").cum_max())
            .with_columns(
                dd=pl.col("equity") / pl.col("running_max") - 1.0,
            )
            .with_columns(
                is_dd=(pl.col("dd") < 0).cast(pl.Int8),
            )
            .with_columns(
                start_edge=(pl.col("is_dd").diff().fill_null(0) == 1).cast(pl.Int32),
            )
            .with_columns(
                seg_raw=pl.col("start_edge").cum_sum(),
            )
            .with_columns(
                seg_id=pl.when(pl.col("is_dd") == 1).then(pl.col("seg_raw")).otherwise(0),
            )
        )

        max_dd_df = lf_dd.select(pl.col("dd").min().alias("max_dd")).collect()
        max_drawdown = max_dd_df["max_dd"].item() if max_dd_df.height > 0 else None

        seg_df = (
            lf_dd.filter(pl.col("seg_id") > 0)
            .group_by("seg_id")
            .agg(
                min_dd=pl.col("dd").min(),
                dur=pl.count(),
            )
            .collect()
        )
        if seg_df.height > 0:
            avg_drawdown = float(pl.Series(seg_df["min_dd"]).mean())
            max_drawdown_duration_days = int(pl.Series(seg_df["dur"]).max())
        else:
            avg_drawdown = None
            max_drawdown_duration_days = 0

        sharpe = None
        if std_daily is not None and std_daily > 0 and mean_daily_return is not None:
            sharpe = mean_daily_return / std_daily

        sortino = None
        if downside_std is not None and downside_std > 0 and mean_daily_return is not None:
            sortino = mean_daily_return / downside_std

        calmar = None
        if annual_return is not None and max_drawdown is not None and abs(max_drawdown) > 0:
            calmar = annual_return / abs(max_drawdown)

        information_ratio = sharpe

        lf_month = (
            lf.sort("time")
            .with_columns(ym=pl.col("time").dt.strftime("%Y-%m"))
            .group_by("ym")
            .agg(equity=pl.col("equity").last())
            .sort("ym")
            .with_columns(ret=pl.col("equity") / pl.col("equity").shift(1) - 1.0)
            .select(["ym", "ret"])
        )
        month_df = lf_month.collect()
        monthly_returns = {
            month_df["ym"].item(i): float(month_df["ret"].item(i))
            for i in range(month_df.height)
            if month_df["ret"].is_not_null().item(i) and pl.select(pl.lit(month_df["ret"].item(i)).is_finite()).item()
        }

        result = {
            "总收益率": float(total_return) if total_return is not None else None,
            "年化收益率": float(annual_return) if annual_return is not None else None,
            "累计收益率": float(total_return) if total_return is not None else None,
            "平均日收益率": float(mean_daily_return) if mean_daily_return is not None else None,
            "月度收益率": monthly_returns,
            "年化波动率": float(vol_annual) if vol_annual is not None else None,
            "下行波动率": float(downside_vol_annual) if downside_vol_annual is not None else None,
            "最大回撤": float(max_drawdown) if max_drawdown is not None else None,
            "平均回撤": float(avg_drawdown) if avg_drawdown is not None else None,
            "回撤持续时间": (int(max_drawdown_duration_days) if max_drawdown_duration_days is not None else 0),
            "夏普比率": float(sharpe) if sharpe is not None else None,
            "索提诺比率": float(sortino) if sortino is not None else None,
            "卡玛比率": float(calmar) if calmar is not None else None,
            "信息比率": float(information_ratio) if information_ratio is not None else None,
        }

        return result

    def print_metrics(self):
        result = self.metrics()
        if result is None:
            return

        def _fmt_pct(v):
            if v is None:
                return "--"
            try:
                return f"{float(v) * 100:.4f}%"
            except Exception:
                return "--"

        mr = result.get("月度收益率") or {}
        mr_items = "\n\t              ".join([f"{k}: {_fmt_pct(mr[k])}" for k in sorted(mr.keys())])
        lines = [
            f"\t    总收益率: {_fmt_pct(result.get('总收益率'))}",
            f"\t  年化收益率: {_fmt_pct(result.get('年化收益率'))}",
            f"\t  累计收益率: {_fmt_pct(result.get('累计收益率'))}",
            f"\t平均日收益率: {_fmt_pct(result.get('平均日收益率'))}",
            f"\t  月度收益率: {mr_items}",
            f"\t  年化波动率: {_fmt_pct(result.get('年化波动率'))}",
            f"\t  下行波动率: {_fmt_pct(result.get('下行波动率'))}",
            f"\t    最大回撤: {_fmt_pct(result.get('最大回撤'))}",
            f"\t    平均回撤: {_fmt_pct(result.get('平均回撤'))}",
            f"\t回撤持续时间: {result.get('回撤持续时间')}",
            f"\t    夏普比率: {result.get('夏普比率')}",
            f"\t  索提诺比率: {result.get('索提诺比率')}",
            f"\t    卡玛比率: {result.get('卡玛比率')}",
            f"\t    信息比率: {result.get('信息比率')}",
        ]

        self.info_log(
            "\n# ================================================================ #\n"
            + "\n".join(lines)
            + "\n# ================================================================ #"
        )
