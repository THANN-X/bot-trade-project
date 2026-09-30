"""ค่าธรรมเนียมและ slippage — ตัวเลขมาจากตัวอย่างใน docs/backtesting.md หัวข้อ 6

ใช้ pytest.approx เพราะทศนิยมในคอมพิวเตอร์ไม่แม่นเป๊ะ (0.1 + 0.2 != 0.3)
"""

import pytest

from tradebot.backtest.costs import apply_slippage, fee

SLIPPAGE = 0.0005  # 0.05% — ค่าใน config/default.yaml
FEE = 0.001  # 0.1%


def test_sell_gets_lower_price():
    """ขายที่ stop 60,000 → ได้จริง 59,970 (หัวข้อ 6 ตัวอย่างแถวแรก)"""
    assert apply_slippage(60_000, "sell", SLIPPAGE) == pytest.approx(59_970)


def test_sell_after_gap():
    """open กระโดดข้าม stop มาที่ 59,500 → ได้จริง 59,470.25 (หัวข้อ 6 แถวที่สอง)"""
    assert apply_slippage(59_500, "sell", SLIPPAGE) == pytest.approx(59_470.25)


def test_buy_pays_higher_price():
    """ซื้อได้แพงกว่าราคาที่เห็นเสมอ"""
    assert apply_slippage(60_000, "buy", SLIPPAGE) == pytest.approx(60_030)


def test_zero_slippage_changes_nothing():
    assert apply_slippage(60_000, "buy", 0) == 60_000
    assert apply_slippage(60_000, "sell", 0) == 60_000


def test_unknown_side_is_rejected():
    """พิมพ์ผิดเป็น "Buy" หรือ "long" ต้อง error ทันที ไม่ใช่เงียบ ๆ แล้วคิดผิดฝั่ง"""
    with pytest.raises(ValueError):
        apply_slippage(60_000, "long", SLIPPAGE)


def test_fee_on_notional():
    """fee คิดจากมูลค่าไม้ (ราคา × จำนวน) — 1 BTC ที่ 59,970 → 59.97 (หัวข้อ 6)"""
    assert fee(59_970, FEE) == pytest.approx(59.97)


def test_fee_example_from_module_docstring():
    """ซื้อ 0.1 BTC ที่ 60,000 = มูลค่า 6,000 → fee 6 USDT"""
    assert fee(6_000, FEE) == pytest.approx(6)
