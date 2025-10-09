from typing import Dict
from .order import Order
from .base import Direction, Volume
from .code import Codes
from decimal import Decimal

class DirectionPosition:
    """方向持仓"""

    code: Codes
    """交易对"""
    direction: Direction
    """交易方向"""
    size: Volume
    """持仓数量"""
    price: Decimal
    """持仓价格"""
    frozen_margin: Decimal
    """冻结保证金"""
    pnl: Decimal
    """未实现盈亏"""

class Position:
    """持仓"""

    code: Codes
    """交易对"""
    frozen_cash: Volume
    """冻结资金"""
    frozen_margin: Decimal
    """冻结保证金"""
    pnl: Decimal
    """未实现盈亏"""
    long: DirectionPosition
    """多头持仓"""
    short: DirectionPosition
    """空头持仓"""
    lever: Decimal
    """杠杆倍数"""
    orders: Dict[str, Order]
    """订单"""
