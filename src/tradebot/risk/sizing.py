"""คำนวณขนาดไม้จากความเสี่ยงต่อไม้ — กฎเต็มอยู่ที่ docs/backtesting.md หัวข้อ 2 "ขนาดไม้"

ตัวอย่าง: พอร์ต 10,000, เสี่ยง 1% = ยอมเสีย 100
ซื้อที่ 60,000 stop loss 59,000 (ห่าง 1,000 ต่อ 1 BTC)
→ ซื้อได้ 100 / 1,000 = 0.1 BTC
"""


def position_size(
    equity: float,
    risk_pct: float,
    entry: float,
    stop: float,
    slippage_pct: float = 0.0,
    fee_pct: float = 0.0,
) -> float:
    """คืนจำนวนเหรียญที่ซื้อ ใช้ค่าที่น้อยกว่าระหว่าง:

    - ตามความเสี่ยง: equity × risk_pct ÷ (entry − stop)
    - ตามเงินที่มี (spot ไม่มี leverage): equity ÷ (entry × (1 + slippage) × (1 + fee))
      คูณกันไม่ใช่บวก เพราะ fee คิดจากราคาหลังบวก slippage แล้ว — แบบบวกจะจ่ายเกินเงินเล็กน้อย

    ถ้าเงินไม่พอซื้อตามความเสี่ยง จะตัดเหลือเท่าที่ซื้อได้ ความเสี่ยงจริงจึงต่ำกว่า risk_pct
    stop ต้องต่ำกว่า entry (long อย่างเดียว) ไม่อย่างนั้น raise ValueError
    """
    risk_amount = equity * risk_pct
    stop_distance = entry - stop

    if stop_distance <= 0:
        raise ValueError(f"stop ต้องต่ำกว่า entry (long) ได้ entry={entry}, stop={stop}")

    coin_amount = risk_amount / stop_distance
    max_coin_amount = equity / (entry * (1 + slippage_pct) * (1 + fee_pct))

    return min(coin_amount, max_coin_amount)
