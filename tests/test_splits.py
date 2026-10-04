"""การแบ่งช่วงข้อมูล — ถ้าตัดผิด ผลทุกรอบผิดตาม และ journal ย้อนแก้ไม่ได้ (backtesting.md หัวข้อ 3)"""

import pytest

from tradebot.backtest.splits import split_slices

SPLITS = {"tune": 0.6, "test": 0.2, "holdout": 0.2}


def test_boundaries_on_round_number():
    s = split_slices(100, SPLITS)
    assert (s["tune"].start, s["tune"].stop) == (0, 60)
    assert (s["test"].start, s["test"].stop) == (60, 80)
    assert (s["holdout"].start, s["holdout"].stop) == (80, 100)


def test_every_row_in_exactly_one_split():
    """ข้อมูลจริง 17,519 แถว — ต่อกันพอดี ไม่ซ้อน ไม่ตกหล่น"""
    n = 17_519
    s = split_slices(n, SPLITS)
    rows = [i for name in ("tune", "test", "holdout") for i in range(n)[s[name]]]
    assert rows == list(range(n))


def test_splits_must_sum_to_one():
    with pytest.raises(ValueError):
        split_slices(100, {"tune": 0.6, "test": 0.3, "holdout": 0.2})
