"""ATR ค่าเฉลี่ยธรรมดา — ค่าคิดมือ, warm-up, gap, look-ahead"""

import pandas as pd
import pytest

from tests.test_lookahead import make_prices
from tradebot.indicators.atr import atr


def hlc(*rows: tuple[float, float, float]) -> pd.DataFrame:
    """แท่งจาก (high, low, close) — ATR ไม่ใช้ open"""
    idx = pd.date_range("2024-01-01", periods=len(rows), freq="1h", tz="UTC")
    df = pd.DataFrame(rows, index=idx, columns=["high", "low", "close"])
    return df.assign(open=df["close"])


# แท่ง   high  low  close  close ก่อน   True Range
#  0      10    8     9      —          NaN (ไม่มี close ก่อนหน้า)
#  1      11    9    10      9          max(2, |11−9|=2, |9−9|=0)   = 2
#  2      14   11    13     10          max(3, |14−10|=4, |11−10|=1) = 4   ← gap ขึ้นทำให้มากกว่า high − low
#  3      13   12   12.5    13          max(1, |13−13|=0, |12−13|=1) = 1
SAMPLE = hlc((10, 8, 9), (11, 9, 10), (14, 11, 13), (13, 12, 12.5))


def test_hand_computed_value():
    """ATR(3) แท่งที่ 3 = (2 + 4 + 1) ÷ 3"""
    assert atr(SAMPLE, 3).iloc[3] == pytest.approx(7 / 3)


def test_warm_up_is_period_plus_one():
    """ATR(3) ต้องมี 4 แท่ง (3 + 1) → แท่ง 0–2 เป็น NaN — ATR(14) จึง warm-up 15 แท่ง"""
    result = atr(SAMPLE, 3)
    assert result.iloc[:3].isna().all()
    assert result.iloc[3:].notna().all()


def test_true_range_includes_gap():
    """แท่ง 2 มี high − low = 3 แต่ True Range = 4 จาก gap — ATR(1) = True Range ของแท่งนั้นพอดี"""
    assert atr(SAMPLE, 1).iloc[2] == pytest.approx(4)


def test_index_matches_input():
    assert atr(SAMPLE, 3).index.equals(SAMPLE.index)


def test_does_not_modify_input():
    before = SAMPLE.copy()
    atr(SAMPLE, 3)
    pd.testing.assert_frame_equal(SAMPLE, before)


@pytest.mark.parametrize("cut", [200, 300, 400])
def test_no_lookahead(cut):
    """ตัดข้อมูลท้ายทิ้ง ค่าในอดีตต้องไม่เปลี่ยน (แบบเดียวกับ tests/test_lookahead.py)"""
    df = make_prices()
    full = atr(df, 14)
    partial = atr(df.iloc[:cut], 14)
    pd.testing.assert_series_equal(partial, full.iloc[:cut])
