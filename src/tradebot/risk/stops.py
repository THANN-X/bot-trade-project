"""คำนวณราคา stop loss ของไม้ long — กฎอยู่ที่ docs/backtesting.md หัวข้อ 6 "ราคา stop"

วิธีเลือกจาก config["risk"]["stop_method"]:
  pct — stop = ราคาเข้าที่ได้จริง × (1 − stop_pct)
  atr — stop = ราคาเข้าที่ได้จริง − atr_mult × ATR ของแท่งสัญญาณ i (ขั้นที่สองของฉาก 2)

ราคาเข้า "ที่ได้จริง" = open แท่ง i+1 หลังบวก slippage แล้ว — ระยะ stop จึงตรงกับเงินที่จ่ายจริง
"""


def stop_price(fill_price: float, risk_cfg: dict, atr: float | None = None) -> float:
    """คืนราคา stop (ต่ำกว่า fill_price เสมอ)

    fill_price — ราคาเข้าที่ได้จริง หลังบวก slippage แล้ว (ความหมายเดียวกับใน sizing)
    risk_cfg   — config["risk"] ที่คนเรียกส่งมา ฟังก์ชันนี้ไม่อ่านไฟล์ config เอง
    atr        — ATR ของแท่งสัญญาณ ใช้เฉพาะ stop_method = "atr"

    stop_method ไม่รู้จัก → raise ValueError แทนที่จะเงียบ ๆ แล้วใช้วิธีอื่น
    """
    method = risk_cfg["stop_method"]

    if method == "pct":
        return fill_price * (1 - risk_cfg["stop_pct"])
    elif method == "atr":
        raise NotImplementedError("stop_method 'atr' ยังไม่ทำ — ขั้นที่สองของฉาก 2")
    else:
        raise ValueError(f"stop_method ต้องเป็น 'pct' หรือ 'atr' ได้ {method!r}")
