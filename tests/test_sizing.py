"""ขนาดไม้จากความเสี่ยงต่อไม้ — กฎอยู่ที่ docs/backtesting.md หัวข้อ 2 "ขนาดไม้"

position_size คืน (size, capped): capped = True เมื่อขนาดถูกตัดด้วยเพดานเงิน
engine ใช้ capped นับ n_capped ลง journal — ให้ sizing เป็นที่เดียวที่รู้สูตร
"""

import pytest

from tradebot.backtest.costs import apply_slippage, fee
from tradebot.risk.sizing import position_size

SLIPPAGE = 0.0005
FEE = 0.001


def test_example_from_docstring():
    """พอร์ต 10,000 เสี่ยง 1% = ยอมเสีย 100; stop ห่าง 1,000 → 0.1 BTC ไม่ชนเพดาน"""
    size, capped = position_size(10_000, 0.01, 60_000, 59_000)
    assert size == pytest.approx(0.1)
    assert capped is False


def test_wider_stop_means_smaller_size():
    """stop 3,000 จากฉาก 0 → 100 ÷ 3,000 ≈ 0.0333 BTC"""
    size, capped = position_size(10_000, 0.01, 84_610, 81_610)
    assert size == pytest.approx(100 / 3_000)
    assert capped is False


def test_loss_at_stop_equals_risk():
    """หัวใจของสูตร: ถ้าโดน stop พอดี ต้องเสียเท่ากับ equity × risk_pct (ยังไม่รวมค่าใช้จ่าย)"""
    size, _ = position_size(10_000, 0.02, 60_000, 58_500)
    assert size * (60_000 - 58_500) == pytest.approx(10_000 * 0.02)


def test_cannot_buy_more_than_equity():
    """spot ไม่มี leverage — stop แคบ 300 ให้ขนาด 0.333 BTC ≈ 28,000 USDT เกินพอร์ต 10,000
    ต้องตัดเหลือเท่าที่เงินพอ: 10,000 ÷ 84,610 (ความเสี่ยงจริงจะต่ำกว่า 1% — ยอมรับได้)
    """
    size, capped = position_size(10_000, 0.01, 84_610, 84_310)
    assert size == pytest.approx(10_000 / 84_610)
    assert size * 84_610 <= 10_000 + 1e-9
    assert capped is True


def test_cap_includes_costs():
    """เพดานต้องเผื่อ slippage และ fee: equity ÷ (entry × (1 + s) × (1 + f))"""
    size, capped = position_size(10_000, 0.01, 84_610, 84_310, SLIPPAGE, FEE)
    assert size == pytest.approx(10_000 / (84_610 * (1 + SLIPPAGE) * (1 + FEE)))
    assert capped is True


def test_cash_never_negative_after_buy():
    """ซื้อตามขนาดที่ได้ แล้วจ่ายจริงผ่าน costs.py — เงินสดที่เหลือต้องไม่ติดลบ
    (สูตรแบบบวก 1 + s + f จะเหลือ −0.005 USDT เพราะ fee คิดจากราคาหลังบวก slippage)
    """
    equity, entry = 10_000, 84_610
    size, _ = position_size(equity, 0.01, entry, 84_310, SLIPPAGE, FEE)

    buy_price = apply_slippage(entry, "buy", SLIPPAGE)
    notional = size * buy_price
    cash_left = equity - notional - fee(notional, FEE)

    assert cash_left >= -1e-9


def test_costs_do_not_change_risk_based_size():
    """stop กว้างพอ (ไม่ชนเพดาน) → ค่าใช้จ่ายไม่ทำให้ขนาดตามความเสี่ยงเปลี่ยน"""
    size, capped = position_size(10_000, 0.01, 60_000, 59_000, SLIPPAGE, FEE)
    assert size == pytest.approx(0.1)
    assert capped is False


def test_stop_equal_to_entry_is_rejected():
    """ระยะ stop = 0 → หารศูนย์ ต้อง error ไม่ใช่คืน inf"""
    with pytest.raises(ValueError):
        position_size(10_000, 0.01, 60_000, 60_000)


def test_stop_above_entry_is_rejected():
    """long อย่างเดียว — stop ต้องอยู่ใต้ราคาเข้า ถ้าอยู่เหนือแปลว่ามีบั๊กที่คนเรียก"""
    with pytest.raises(ValueError):
        position_size(10_000, 0.01, 60_000, 61_000)
