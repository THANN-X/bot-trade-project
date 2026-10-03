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
