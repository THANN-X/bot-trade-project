"""คำนวณขนาดไม้จากความเสี่ยงต่อไม้

ตัวอย่าง: พอร์ต 10,000, เสี่ยง 1% = ยอมเสีย 100
ซื้อที่ 60,000 stop loss 59,000 (ห่าง 1,000 ต่อ 1 BTC)
→ ซื้อได้ 100 / 1,000 = 0.1 BTC
"""


def position_size(equity: float, risk_pct: float, entry: float, stop: float) -> float:
    """คืนจำนวนเหรียญที่ซื้อได้

    TODO(ฉาก 2): อย่าลืมกรณี entry == stop (หารศูนย์) และ stop อยู่ผิดฝั่ง
    """
    raise NotImplementedError
