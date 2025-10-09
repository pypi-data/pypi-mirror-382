from .position import Position
from .code import Codes
from datetime import datetime
from decimal import Decimal

class Candle:
    """K线"""

    time: datetime
    """时间"""
    open: Decimal
    """开盘价"""
    high: Decimal
    """最高价"""
    low: Decimal
    """最低价"""
    close: Decimal
    """收盘价"""
    volume: Decimal
    """成交量"""
    finish: bool
    """是否完成"""

class FundingRate:
    """资金费率"""

    code: Codes
    """交易对"""
    time: datetime
    """时间"""
    rate: Decimal
    """资金费率"""
    next_time: datetime
    """下次结算时间"""
    min: Decimal
    """最小资金费率"""
    max: Decimal
    """最大资金费率"""
    update_time: datetime
    """更新时间"""

class Symbol:
    """交易对"""

    code: Codes
    """交易对"""
    taker: Decimal
    """吃单费率"""
    maker: Decimal
    """挂单费率"""
    position: Position
    """持仓"""
    last_price: Decimal
    """最新价"""
