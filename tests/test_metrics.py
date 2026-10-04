"""ทดสอบสูตร metrics ด้วยตัวเลขที่คิดมือได้ — นิยามอยู่ใน CLAUDE.md หัวข้อ "ตัวชี้วัด"

ทำไมสำคัญ: ถ้าสูตรผิด ทุกการตัดสินใจหลังจากนี้ผิดหมด
และเป็นส่วนที่ทดสอบง่ายสุด (input ตายตัว → output ตายตัว)

ข้อตกลงที่ test กำหนด:
- ไม้ "ชนะ" = pnl > 0 · ไม้ "ไม่ชนะ" = pnl ≤ 0 (เสมอทุนนับเป็นไม่ชนะ — หลังหักค่าใช้จ่ายเกิดยากมาก)
- ไม่มีไม้เลย → ทุกตัวคืน 0 (ไม่ error, ไม่ NaN — journal ต้องเขียนได้เสมอ)
- max_drawdown และ worst_day_pct คืนเป็นสัดส่วนบวก "เสียไปเท่าไหร่" เช่น 0.25 = 25%
"""

import math

import pandas as pd
import pytest

from tradebot.backtest.engine import Trade
from tradebot.backtest.metrics import (
    by_exit_reason,
    expectancy,
    max_drawdown,
    max_losing_streak,
    net_profit,
    profit_factor,
    total_costs,
    win_rate,
    worst_day_pct,
)


def trades(*pnls: float) -> list[Trade]:
    """สร้างไม้จาก pnl อย่างเดียว — metrics ใช้แค่ pnl ฟิลด์อื่นใส่ค่าหลอกไว้"""
    t = pd.Timestamp("2024-01-01", tz="UTC")
    return [Trade(t, t, 100.0, 100.0, 1.0, p, 0.0, "signal") for p in pnls]


EXAMPLE = trades(100, -50, 30, -20)  # ตัวอย่างหลัก: ชนะ 130, แพ้ 70


# ── ฉาก 2: 5 ตัวหลัก ─────────────────────────────────────────────────────────
def test_net_profit():
    assert net_profit(EXAMPLE) == pytest.approx(60)


def test_expectancy():
    """กำไรสุทธิ ÷ จำนวนไม้ = 60 ÷ 4"""
    assert expectancy(EXAMPLE) == pytest.approx(15)


def test_profit_factor():
    """กำไรรวมไม้ชนะ ÷ ขาดทุนรวมไม้แพ้ = 130 ÷ 70 (ขาดทุนใช้ค่าบวก ไม่ใช่ −70)"""
    assert profit_factor(EXAMPLE) == pytest.approx(130 / 70)


def test_profit_factor_without_losers_is_infinite():
    """ไม่มีไม้แพ้ = หารศูนย์ → ทางคณิตศาสตร์คือไม่มีที่สิ้นสุด (float('inf'))"""
    assert math.isinf(profit_factor(trades(10, 20)))


def test_win_rate():
    """ชนะ 2 จาก 4 ไม้"""
    assert win_rate(EXAMPLE) == pytest.approx(0.5)


def test_break_even_is_not_a_win():
    assert win_rate(trades(10, 0)) == pytest.approx(0.5)


def test_no_trades_returns_zero_everywhere():
    """backtest ที่ไม่มีไม้เลยก็ต้องบันทึก journal ได้ — ห้าม error เพราะหารศูนย์"""
    assert net_profit([]) == 0
    assert expectancy([]) == 0
    assert profit_factor([]) == 0
    assert win_rate([]) == 0
    assert max_losing_streak([]) == 0


def test_max_drawdown():
    """จุดสูงสุด 120 แล้วลงไปต่ำสุด 80 = เสีย 40 ÷ 120 = 1/3
    (ลง 120 → 90 = 25% ก็จริง แต่ไม่ใช่ครั้งที่ลึกที่สุด)
    """
    equity = pd.Series([100, 120, 90, 110, 80, 130.0])
    assert max_drawdown(equity) == pytest.approx(1 / 3)


def test_max_drawdown_measured_from_running_peak():
    """จุดสูงสุดต้องเป็น "สูงสุดจนถึงตอนนั้น" ไม่ใช่สูงสุดของทั้งชุด
    ลงจาก 100 → 50 ก่อนจะขึ้นไป 200 = 50% (ถ้าใช้ 200 เป็นจุดสูงสุดจะผิด)
    """
    equity = pd.Series([100, 50, 200.0])
    assert max_drawdown(equity) == pytest.approx(0.5)


def test_max_drawdown_never_down_is_zero():
    assert max_drawdown(pd.Series([100, 110, 120.0])) == 0


# ── ฉาก 3: สำหรับตั้ง kill switch (journal ต้องใช้ตั้งแต่รอบแรก) ─────────────
def test_max_losing_streak():
    """+ − − + − − − + → แพ้ติดกันยาวสุด 3"""
    assert max_losing_streak(trades(10, -5, -5, 10, -5, -5, -5, 10)) == 3


def test_losing_streak_counts_break_even():
    """เสมอทุนนับเป็นไม่ชนะ (ข้อตกลงเดียวกับ win_rate)"""
    assert max_losing_streak(trades(10, -5, 0, -5, 10)) == 3


def test_worst_day_pct():
    """วันตัดที่ 00:00 UTC — เทียบ equity ปลายวันกับปลายวันก่อนหน้า
    วันแรกเทียบกับ equity จุดแรกของกราฟ (ทุนเริ่มต้น)

    วัน 1: 10,000 → 9,800  (−2%)
    วัน 2:  9,800 → 9,310  (−5%)   ← แย่สุด
    วัน 3:  9,310 → 9,500  (+2.04%)
    """
    idx = pd.to_datetime(
        [
            "2024-01-01 22:00",
            "2024-01-01 23:00",
            "2024-01-02 12:00",
            "2024-01-02 23:00",
            "2024-01-03 05:00",
            "2024-01-03 23:00",
        ],
        utc=True,
    )
    equity = pd.Series([10_000, 9_800, 9_000, 9_310, 9_900, 9_500.0], index=idx)
    assert worst_day_pct(equity) == pytest.approx(0.05)


def test_worst_day_ignores_intraday_dip():
    """วัน 2 ลงไป 9,000 ระหว่างวันแต่ปิดวันที่ 9,310 → นับแค่ปลายวัน (ดู test ข้างบน)
    ทุกวันกำไร → 0
    """
    idx = pd.to_datetime(["2024-01-01 10:00", "2024-01-01 23:00", "2024-01-02 23:00"], utc=True)
    assert worst_day_pct(pd.Series([10_000, 10_100, 10_200.0], index=idx)) == 0


# ── รายละเอียดสำหรับวิเคราะห์ว่าทำไมกำไร/ขาดทุน ──────────────────────────────
def test_by_exit_reason():
    t = pd.Timestamp("2024-01-01", tz="UTC")
    mixed = [
        Trade(t, t, 100.0, 98.0, 1.0, -100.0, 0.0, "stop"),
        Trade(t, t, 100.0, 98.0, 1.0, -90.0, 0.0, "stop"),
        Trade(t, t, 100.0, 105.0, 1.0, 50.0, 0.0, "signal"),
    ]
    assert by_exit_reason(mixed) == {
        "signal": {"n": 1, "pnl": pytest.approx(50.0)},
        "stop": {"n": 2, "pnl": pytest.approx(-190.0)},
        "end": {"n": 0, "pnl": 0.0},  # ไม่มีไม้ก็ต้องมี key ครบ
    }


def test_total_costs():
    t = pd.Timestamp("2024-01-01", tz="UTC")
    two = [
        Trade(t, t, 100.0, 100.0, 1.0, 0.0, 10.0, "signal", slippage=5.0),
        Trade(t, t, 100.0, 100.0, 1.0, 0.0, 12.0, "stop", slippage=6.0),
    ]
    assert total_costs(two) == {"fees": 22.0, "slippage": 11.0, "total": 33.0}
    assert total_costs([]) == {"fees": 0, "slippage": 0, "total": 0}
