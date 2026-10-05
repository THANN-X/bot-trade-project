"""คำนวณราคา stop loss ของไม้ long — กฎอยู่ที่ docs/backtesting.md หัวข้อ 6 "ราคา stop"

วิธีเลือกจาก config["risk"]["stop_method"]:
  pct — stop = ราคาเข้าที่ได้จริง × (1 − stop_pct)
  atr — stop = ราคาเข้าที่ได้จริง − atr_mult × ATR ของแท่งสัญญาณ i (indicators/atr.py)

ราคาเข้า "ที่ได้จริง" = open แท่ง i+1 หลังบวก slippage แล้ว — ระยะ stop จึงตรงกับเงินที่จ่ายจริง
"""

import math


def stop_price(fill_price: float, risk_cfg: dict, atr: float | None = None) -> float:
    """คืนราคา stop (ต่ำกว่า fill_price เสมอ)

    fill_price — ราคาเข้าที่ได้จริง หลังบวก slippage แล้ว (ความหมายเดียวกับใน sizing)
    risk_cfg   — config["risk"] ที่คนเรียกส่งมา ฟังก์ชันนี้ไม่อ่านไฟล์ config เอง
    atr        — ATR ของแท่งสัญญาณ ใช้เฉพาะ stop_method = "atr"

    stop_method ไม่รู้จัก → raise ValueError แทนที่จะเงียบ ๆ แล้วใช้วิธีอื่น
    atr เป็น None / NaN / ≤ 0 → raise ValueError (เช็ค None ก่อน — or หยุดที่ True ตัวแรก
    จึงไม่เรียก math.isnan(None) ซึ่งจะเป็น TypeError)
    """
    method = risk_cfg["stop_method"]

    if method == "pct":
        return fill_price * (1 - risk_cfg["stop_pct"])
    elif method == "atr":
        if atr is None or math.isnan(atr) or atr <= 0:
            raise ValueError(
                f"stop_method = atr ต้องได้ ATR เป็นตัวเลขบวก ได้ {atr!r} "
                "(ไม่ได้ส่งมา / ยังอยู่ช่วง warm-up / ข้อมูลผิด)"
            )
        return fill_price - risk_cfg["atr_mult"] * atr
    else:
        raise ValueError(f"stop_method ต้องเป็น 'pct' หรือ 'atr' ได้ {method!r}")
