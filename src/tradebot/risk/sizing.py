"""คำนวณขนาดไม้จากความเสี่ยงต่อไม้ — กฎเต็มอยู่ที่ docs/backtesting.md หัวข้อ 2 "ขนาดไม้"

ตัวอย่าง: พอร์ต 10,000, เสี่ยง 1% = ยอมเสีย 100
ซื้อที่ 60,000 stop loss 59,000 (ห่าง 1,000 ต่อ 1 BTC)
→ ซื้อได้ 100 / 1,000 = 0.1 BTC
"""


def position_size(
    equity: float,
    risk_pct: float,
    fill_price: float,
    stop: float,
    fee_pct: float = 0.0,
) -> tuple[float, bool]:
    """คืนจำนวนเหรียญที่ซื้อ ใช้ค่าที่น้อยกว่าระหว่าง:

    - ตามความเสี่ยง: equity × risk_pct ÷ (fill_price − stop)
    - ตามเงินที่มี (spot ไม่มี leverage): equity ÷ (fill_price × (1 + fee))

    fill_price — ราคาเข้าที่ได้จริง หลังบวก slippage แล้ว (engine คำนวณก่อนเรียก)
                 ฟังก์ชันนี้จึงไม่รับ slippage — ถ้ารับจะนับ slippage ซ้ำสองรอบ
    fee_pct    — fee คิดจากมูลค่าหลังบวก slippage จึงคูณกับ fill_price ตรง ๆ

    ถ้าเงินไม่พอซื้อตามความเสี่ยง จะตัดเหลือเท่าที่ซื้อได้ ความเสี่ยงจริงจึงต่ำกว่า risk_pct
    คืน (size, capped) — capped = True เมื่อถูกตัดด้วยเพดานเงิน (engine ใช้นับ n_capped)
    stop ต้องต่ำกว่า fill_price (long อย่างเดียว) ไม่อย่างนั้น raise ValueError
    """
    risk_amount = equity * risk_pct
    stop_distance = fill_price - stop

    if stop_distance <= 0:
        raise ValueError(f"stop ต้องต่ำกว่าราคาเข้า (long) ได้ fill_price={fill_price}, stop={stop}")

    coin_amount = risk_amount / stop_distance
    max_coin_amount = equity / (fill_price * (1 + fee_pct))
    size = min(coin_amount, max_coin_amount)
    capped = coin_amount > max_coin_amount

    # ราคาจาก DataFrame เป็น numpy.float64 → ผลเปรียบเทียบเป็น numpy bool
    # แปลงเป็นชนิดของ Python ให้ตรงกับ type hint (n_capped จะได้เป็น int ไม่ใช่ numpy int64)
    return float(size), bool(capped)
