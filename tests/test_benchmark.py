"""buy & hold — เกณฑ์เทียบของทุกรอบ ค่าใช้จ่ายต้องคิดแบบเดียวกับ engine"""

import pandas as pd
import pytest

from tradebot.backtest.benchmark import buy_and_hold


def bars(*ohlc):
    idx = pd.date_range("2024-01-01", periods=len(ohlc), freq="1h", tz="UTC")
    return pd.DataFrame(ohlc, index=idx, columns=["open", "high", "low", "close"])


DF = bars(
    (100.0, 101.0, 99.0, 100.0),  # ซื้อที่ open 100
    (100.0, 100.5, 89.0, 90.0),  # ระหว่างทางลงไป close 90
    (90.0, 111.0, 89.5, 110.0),  # ขายที่ close 110
)


def test_no_costs():
    """ทุน 10,000 ซื้อที่ 100 = 100 เหรียญ → ขาย 110 = 11,000 → +10%"""
    result = buy_and_hold(DF, 10_000, 0.0, 0.0)
    assert result["net_profit"] == pytest.approx(1_000)
    assert result["return_pct"] == pytest.approx(0.10)


def test_drawdown_while_holding():
    """equity: 10,000 → 10,000 → 9,000 → 11,000 → ลงจากจุดสูงสุด 10%"""
    assert buy_and_hold(DF, 10_000, 0.0, 0.0)["max_drawdown"] == pytest.approx(0.10)


def test_costs_on_both_legs():
    """ซื้อ 100 × 1.0005, fee จากมูลค่าหลัง slippage; ขาย 110 × 0.9995 − fee"""
    s, f = 0.0005, 0.001
    size = 10_000 / (100 * (1 + s) * (1 + f))
    proceeds = size * 110 * (1 - s) * (1 - f)

    result = buy_and_hold(DF, 10_000, s, f)

    assert result["net_profit"] == pytest.approx(proceeds - 10_000)
    assert result["net_profit"] < 1_000  # ค่าใช้จ่ายทำให้ได้น้อยกว่าแบบไม่มีค่าใช้จ่ายเสมอ
