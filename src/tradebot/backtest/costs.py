"""ค่าธรรมเนียมและ slippage — backtest ที่ไม่หักสองอย่างนี้เชื่อไม่ได้

ตัวอย่าง: ซื้อ 0.1 BTC ที่ 60,000 (มูลค่า 6,000) fee 0.1% = 6 USDT
เข้า+ออก = ~12 USDT ต่อไม้ ถ้าเทรด 300 ไม้ = 3,600 USDT
"""


def apply_slippage(price: float, side: str, slippage_pct: float) -> float:
    """ซื้อได้แพงกว่า ขายได้ถูกกว่าราคาที่เห็นเสมอ

    TODO(ฉาก 2)
    """
    raise NotImplementedError


def fee(notional: float, fee_pct: float) -> float:
    """TODO(ฉาก 2)"""
    raise NotImplementedError
