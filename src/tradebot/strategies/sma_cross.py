"""SMA crossover: เส้นเร็วตัดขึ้นเส้นช้า = ซื้อ, ตัดลง = ขาย

สัญญาณแบบ "เหตุการณ์" (event): BUY/SELL เฉพาะแท่งที่เส้นตัดกัน แท่งอื่นเป็น HOLD
พฤติกรรมที่ตั้งใจ (ไม่ใช่บั๊ก):
  - ต้นข้อมูลหรือต้นช่วง ถ้า SMA20 อยู่เหนือ SMA50 อยู่แล้ว → ไม่ซื้อ รอจุดตัดขึ้นครั้งถัดไป
  - โดน stop loss กลางขาขึ้น → ไม่มีจุดตัดใหม่ จึงไม่กลับเข้า จนกว่าจะตัดลงแล้วตัดขึ้นอีกรอบ

แบบ "สถานะ" (ควรถือ long ทุกแท่งที่ fast > slow) ให้ผลต่างกันจริง — ตัดสินที่ฉาก 5
ดู docs/decisions/0002-hexagonal-at-stage-5.md
"""

import pandas as pd

from tradebot.strategies.base import Signal, Strategy


class SmaCross(Strategy):
    name = "sma_cross"

    def __init__(self, fast: int = 20, slow: int = 50):
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        - คำนวณ SMA fast/slow จาก close
        - หาจุดที่ "ตัดกัน" (ไม่ใช่แค่ fast > slow — ต่างกันยังไง?)
        - ช่วงแรกที่ SMA ยังคำนวณไม่ได้ (NaN) ต้องเป็น HOLD
        """
        fast = df["close"].rolling(self.fast).mean()
        slow = df["close"].rolling(self.slow).mean()

        above = fast > slow
        prev_above = above.shift(1, fill_value=False)

        ready = slow.notna() & slow.shift(1).notna()
        cross_up = ready & above & ~prev_above
        cross_down = ready & ~above & prev_above

        signals = pd.Series(Signal.HOLD, index=df.index)
        signals[cross_up] = Signal.BUY
        signals[cross_down] = Signal.SELL

        return signals
