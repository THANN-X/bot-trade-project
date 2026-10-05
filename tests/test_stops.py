"""ราคา stop — กฎอยู่ที่ docs/backtesting.md หัวข้อ 6 "ราคา stop"

ขั้นแรก: pct เท่านั้น — test ของ atr จะเพิ่มในขั้นที่สองของฉาก 2
"""

import pytest

from tradebot.risk.stops import stop_price

PCT = {"stop_method": "pct", "stop_pct": 0.02}


def test_pct_below_entry():
    """เข้าได้จริง 100 → stop 2% = 98"""
    assert stop_price(100, PCT) == pytest.approx(98)


def test_pct_measured_from_fill_price():
    """ราคาเข้าที่ได้จริงรวม slippage แล้ว เช่น open 60,000 + 0.05% = 60,030 → stop 58,829.4"""
    assert stop_price(60_030, PCT) == pytest.approx(60_030 * 0.98)


def test_pct_ignores_atr():
    """ส่ง atr มาก็ไม่ใช้ ถ้าวิธีเป็น pct"""
    assert stop_price(100, PCT, atr=5) == pytest.approx(98)


def test_unknown_method_is_rejected():
    """พิมพ์ผิดใน config ต้อง error ทันที ไม่ใช่เงียบ ๆ แล้วใช้วิธีอื่น"""
    with pytest.raises(ValueError):
        stop_price(100, {"stop_method": "percent", "stop_pct": 0.02})


# ── atr (ขั้นที่สองของฉาก 2) ──────────────────────────────────────────────────
ATR = {"stop_method": "atr", "atr_period": 14, "atr_mult": 2}


def test_atr_below_entry_by_multiple():
    """เข้าได้จริง 100, ATR 1.5, ตัวคูณ 2 → stop = 100 − 3 = 97"""
    assert stop_price(100, ATR, atr=1.5) == pytest.approx(97)


@pytest.mark.parametrize("bad_atr", [None, float("nan"), 0.0, -1.0])
def test_atr_missing_or_invalid_is_rejected(bad_atr):
    """ไม่มี ATR / ยังอยู่ช่วง warm-up (NaN) / ไม่เป็นบวก → error ทันที
    ถ้าปล่อยผ่าน stop จะเท่ากับราคาเข้า (หรือสูงกว่า) แล้ว sizing จะ error ทีหลังแบบงง ๆ
    """
    with pytest.raises(ValueError):
        stop_price(100, ATR, atr=bad_atr)
