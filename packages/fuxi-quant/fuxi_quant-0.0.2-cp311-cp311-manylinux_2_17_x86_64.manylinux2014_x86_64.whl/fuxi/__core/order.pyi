from typing import Optional
from .base import Direction, OrderStatus, Side
from .code import Codes
from datetime import datetime
from decimal import Decimal

class Order:
    """订单"""

    code: Codes
    """交易对"""
    id: str
    """订单id"""
    direction: Direction
    """交易方向"""
    side: Side
    """买卖方向"""
    status: OrderStatus
    """订单状态"""
    size: Decimal
    """订单数量"""
    price: Decimal
    """订单价格"""
    deal_size: Decimal
    """成交数量"""
    deal_price: Decimal
    """成交价格"""
    deal_fee: Decimal
    """成交手续费"""
    frozen_cash: Decimal
    """冻结资金"""
    frozen_margin: Decimal
    """冻结保证金"""
    remark: Optional[str]
    """备注"""
    create_time: datetime
    """创建时间"""
    update_time: datetime
    """更新时间"""
