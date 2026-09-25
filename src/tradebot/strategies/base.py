"""สัญญา (interface) ที่ทุกกลยุทธ์ต้องทำตาม

ทำไมต้องมี: ให้ backtest engine และตัวส่งคำสั่งบน testnet เรียกกลยุทธ์ได้
แบบเดียวกัน — เขียนกลยุทธ์ครั้งเดียว ใช้ได้ทั้งสองที่

กลยุทธ์บอกได้แค่ "อยากทำอะไร" ส่วนจะทำได้ไหมและเท่าไหร่ risk/ เป็นคนตัดสิน

กฎ: โค้ดบริสุทธิ์ — ห้าม I/O (ไม่อ่านไฟล์, ไม่เรียก exchange, ไม่ใช้เวลาปัจจุบัน)
และห้าม import data/, backtest/, live/ — ดู docs/architecture.md
"""

from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd


class Signal(Enum):
    BUY = 1
    SELL = -1
    HOLD = 0


class Strategy(ABC):
    name: str = "base"

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """รับ OHLCV คืน Series ของ Signal หนึ่งค่าต่อแท่ง (index เดียวกับ df)

        กฎ look-ahead: สัญญาณของแท่ง i ใช้ข้อมูลได้ถึงแท่ง i เท่านั้น
        engine จะเข้าออเดอร์ที่ราคา open ของแท่ง i+1
        """
