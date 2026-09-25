"""ตัวชี้วัดผล backtest — นิยามอยู่ใน CLAUDE.md หัวข้อ "ตัวชี้วัดหลัก"

สองตัวท้าย (max_losing_streak, worst_day_pct) ใช้ตั้งเพดาน kill switch
"""

import pandas as pd

from tradebot.backtest.engine import Trade


def net_profit(trades: list[Trade]) -> float:
    """TODO(ฉาก 2)"""
    raise NotImplementedError


def expectancy(trades: list[Trade]) -> float:
    """กำไรสุทธิ ÷ จำนวนไม้ — TODO(ฉาก 2)"""
    raise NotImplementedError


def profit_factor(trades: list[Trade]) -> float:
    """กำไรรวมไม้ชนะ ÷ ขาดทุนรวมไม้แพ้

    TODO(ฉาก 2): ถ้าไม่มีไม้แพ้เลยจะคืนอะไร?
    """
    raise NotImplementedError


def max_drawdown(equity_curve: pd.Series) -> float:
    """ลดลงจากจุดสูงสุดมากที่สุดกี่ % — TODO(ฉาก 2)"""
    raise NotImplementedError


def win_rate(trades: list[Trade]) -> float:
    """ใช้ประกอบเท่านั้น — TODO(ฉาก 2)"""
    raise NotImplementedError


def max_losing_streak(trades: list[Trade]) -> int:
    """แพ้ติดกันมากสุดกี่ไม้ → ใช้ตั้ง kill_switch.losing_streak — TODO(ฉาก 3)"""
    raise NotImplementedError


def worst_day_pct(equity_curve: pd.Series) -> float:
    """ขาดทุนของวันที่แย่ที่สุด (วันตัดที่ 00:00 UTC) → ใช้ตั้ง kill_switch.daily_loss

    TODO(ฉาก 3)
    """
    raise NotImplementedError
