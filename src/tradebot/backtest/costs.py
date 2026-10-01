"""ค่าธรรมเนียมและ slippage — backtest ที่ไม่หักสองอย่างนี้เชื่อไม่ได้

กฎอยู่ที่ docs/backtesting.md หัวข้อ 2 และ 6 — หัก slippage ก่อน แล้วคิด fee
จากมูลค่าหลังหัก slippage

ตัวอย่าง: ซื้อ 0.1 BTC ที่ 60,000 (มูลค่า 6,000) fee 0.1% = 6 USDT
เข้า+ออก = ~12 USDT ต่อไม้ ถ้าเทรด 300 ไม้ = 3,600 USDT
"""


def apply_slippage(price: float, side: str, slippage_pct: float) -> float:
    """คืนราคาที่ได้จริง: ซื้อแพงขึ้น ขายถูกลงเสมอ

    side ต้องเป็น "buy" หรือ "sell" เท่านั้น — ค่าอื่น raise ValueError
    แทนที่จะเงียบ ๆ แล้วคิดผิดฝั่ง
    """
    if side == "buy":
        return price * (1 + slippage_pct)
    elif side == "sell":
        return price * (1 - slippage_pct)
    else:
        raise ValueError(f"Invalid side. Expected 'buy' or 'sell'. got {side!r}")


def fee(notional: float, fee_pct: float) -> float:
    """ค่าธรรมเนียมของไม้มูลค่า notional (ราคาหลังหัก slippage × จำนวนเหรียญ)"""
    return notional * fee_pct
