"""ตรวจ look-ahead bias อัตโนมัติ — ทุกกลยุทธ์ต้องผ่านก่อนนับผล backtest

หลักการ (docs/backtesting.md หัวข้อ 1):
  1. คำนวณสัญญาณจากข้อมูลเต็ม
  2. ตัดข้อมูลท้ายทิ้ง แล้วคำนวณใหม่
  3. สัญญาณช่วงที่ซ้อนกันต้องเหมือนเดิมทุกจุด
     ถ้าเปลี่ยน = สัญญาณในอดีตขึ้นกับข้อมูลอนาคต

ใช้ได้เพราะ strategy เป็นโค้ดบริสุทธิ์ (DataFrame เข้า → สัญญาณออก)
เพิ่มกลยุทธ์ใหม่: เติมลงใน STRATEGIES ที่เดียว

ลองทำให้ fail ดูหนึ่งครั้ง: ใส่ .shift(-1) ในกลยุทธ์ แล้วรัน pytest ดูว่าจับได้ไหม
"""

import numpy as np
import pandas as pd
import pytest

from tradebot.strategies.base import Signal
from tradebot.strategies.sma_cross import SmaCross

STRATEGIES = [SmaCross(20, 50)]
CUTS = [200, 300, 400]


def make_prices(n: int = 500, seed: int = 42) -> pd.DataFrame:
    """ราคาปลอมแบบ random walk — seed ตายตัว ได้ข้อมูลเดิมทุกครั้ง ไม่พึ่งไฟล์หรือเน็ต"""
    rng = np.random.default_rng(seed)
    close = 100 + rng.normal(0, 1, n).cumsum()
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": 1.0},
        index=idx,
    )


@pytest.mark.parametrize("strategy", STRATEGIES, ids=lambda s: s.name)
@pytest.mark.parametrize("cut", CUTS)
def test_no_lookahead(strategy, cut):
    """สัญญาณของ cut แท่งแรกต้องไม่เปลี่ยน เมื่อมีข้อมูลหลังจากนั้นเพิ่มเข้ามา"""
    df = make_prices()

    full = strategy.generate_signals(df)
    partial = strategy.generate_signals(df.iloc[:cut])

    pd.testing.assert_series_equal(partial, full.iloc[:cut])


@pytest.mark.parametrize("strategy", STRATEGIES, ids=lambda s: s.name)
def test_fixture_has_signals(strategy):
    """กัน test ข้างบนผ่านแบบไม่ได้ทดสอบอะไร — ถ้าไม่มีจุดตัดเลย HOLD ทุกแถวก็เท่ากันเสมอ"""
    signals = strategy.generate_signals(make_prices())

    assert (signals == Signal.BUY).any()
    assert (signals == Signal.SELL).any()


@pytest.mark.parametrize("strategy", STRATEGIES, ids=lambda s: s.name)
def test_does_not_modify_input(strategy):
    """strategy ต้องไม่แก้ DataFrame ที่รับเข้ามา (docs/architecture.md — โค้ดบริสุทธิ์)"""
    df = make_prices()
    before = df.copy()

    strategy.generate_signals(df)

    pd.testing.assert_frame_equal(df, before)
