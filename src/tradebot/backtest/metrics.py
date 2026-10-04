"""ตัวชี้วัดผล backtest — นิยามอยู่ใน CLAUDE.md หัวข้อ "ตัวชี้วัด"

ข้อตกลง (tests/test_metrics.py):
- ไม้ "ชนะ" = pnl > 0 · เสมอทุนนับเป็นไม่ชนะ
- ไม่มีไม้เลย → คืน 0 ทุกตัว (journal ต้องเขียนได้เสมอ)
- max_drawdown / worst_day_pct คืนสัดส่วนบวก "เสียไปเท่าไหร่" เช่น 0.25 = 25%

สองตัวท้าย (max_losing_streak, worst_day_pct) ใช้ตั้งเพดาน kill switch
"""

import pandas as pd

from tradebot.backtest.engine import Trade


def net_profit(trades: list[Trade]) -> float:
    """กำไรสุทธิรวมทุกไม้ (pnl หลังหักค่าใช้จ่ายแล้ว)"""
    pnls = (t.pnl for t in trades)
    return sum(pnls)


def expectancy(trades: list[Trade]) -> float:
    """กำไรสุทธิ ÷ จำนวนไม้ — ต้องเป็นบวก กลยุทธ์ถึงจะมีกำไรหลังหักค่าใช้จ่าย"""
    if not trades:
        return 0.0
    return net_profit(trades) / len(trades)


def profit_factor(trades: list[Trade]) -> float:
    """กำไรรวมไม้ชนะ ÷ ขาดทุนรวมไม้แพ้ (ค่าบวก) — ต่ำกว่า 1 = เสียเงิน

    ไม่มีไม้แพ้เลย → float("inf") · ไม่มีไม้เลย → 0
    """
    if not trades:
        return 0.0

    wins = sum(t.pnl for t in trades if t.pnl > 0)
    losses = -sum(t.pnl for t in trades if t.pnl < 0)

    if losses == 0:
        return float("inf")
    return wins / losses


def max_drawdown(equity_curve: pd.Series) -> float:
    """ลดลงจากจุดสูงสุด "จนถึงตอนนั้น" มากที่สุดกี่ส่วน (cummax — ไม่แอบดูจุดสูงสุดในอนาคต)"""
    cumulative_max = equity_curve.cummax()
    drawdown = 1 - (equity_curve / cumulative_max)
    return float(drawdown.max())


def win_rate(trades: list[Trade]) -> float:
    """สัดส่วนไม้ที่ pnl > 0 — ใช้ประกอบเท่านั้น ไม่ใช่ตัวตัดสิน"""
    if not trades:
        return 0.0
    wins = [t.pnl for t in trades if t.pnl > 0]
    return len(wins) / len(trades)


def max_losing_streak(trades: list[Trade]) -> int:
    """ไม้ไม่ชนะ (pnl ≤ 0) ติดกันมากสุดกี่ไม้ → ใช้ตั้ง kill_switch.losing_streak"""
    current_streak = 0
    max_streak = 0
    for t in trades:
        if t.pnl <= 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    return max_streak


def worst_day_pct(equity_curve: pd.Series) -> float:
    """ขาดทุนของวันที่แย่ที่สุด → ใช้ตั้ง kill_switch.daily_loss

    วันตัดที่ 00:00 UTC — เทียบ equity ปลายวันกับปลายวันก่อนหน้า
    วันแรกเทียบกับ equity จุดแรก (ทุนเริ่มต้น) · ไม่มีวันขาดทุน → 0
    """
    daily = equity_curve.resample("1D").last()
    prev = daily.shift(1, fill_value=equity_curve.iloc[0])
    percent_change = daily / prev - 1
    worst_day = -(percent_change.min())
    return max(0.0, float(worst_day))
