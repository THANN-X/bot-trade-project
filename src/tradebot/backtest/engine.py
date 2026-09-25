"""Backtest engine — เดินทีละแท่ง จำลองการเข้า/ออกออเดอร์

กฎทั้งหมดอยู่ใน docs/backtesting.md ที่เดียว — ที่นี่เป็นแค่สรุปพร้อมเลขหัวข้อ
ถ้ากฎเปลี่ยน แก้ที่ backtesting.md ก่อน แล้วค่อยแก้โค้ดให้ตรง

รับสัญญาณที่คำนวณจากข้อมูลเต็มมาแล้ว ไม่คำนวณใหม่ (หัวข้อ 3, 5)

ลำดับต่อแท่ง:
  1. อ่านสัญญาณของแท่งก่อนหน้า (ที่ปิดแล้ว)                     — หัวข้อ 1
  2. ถ้ามีสัญญาณ → ถาม risk/ ว่าเข้าได้ไหม ขนาดเท่าไหร่
  3. เข้าออเดอร์ที่ open ของแท่งนี้ + หัก fee/slippage (costs.py)  — หัวข้อ 2
  4. เช็ค stop loss: open ข้าม stop → ปิดที่ open, ไม่งั้น low แตะ → ปิดที่ stop
     แท่งที่เพิ่งเข้าไม้เช็คแค่ low                                  — หัวข้อ 6
  5. แจ้ง kill switch เมื่อปิดไม้

หลังโดน stop รอ BUY ครั้งถัดไป, SELL ตอนไม่มีไม้ = ไม่ทำอะไร        — หัวข้อ 6
รอยต่อช่วง: พอร์ตว่างตอนเริ่ม, ปิดไม้ค้างที่ close แท่งสุดท้าย,
ไม่ใช้สัญญาณแท่งสุดท้าย                                            — หัวข้อ 3
"""

from dataclasses import dataclass, field

import pandas as pd

from tradebot.strategies.base import Strategy


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float
    exit_price: float
    size: float
    pnl: float  # หลังหักค่าธรรมเนียมแล้ว
    fees: float


@dataclass
class BacktestResult:
    trades: list[Trade] = field(default_factory=list)
    equity_curve: pd.Series | None = None


def run_backtest(df: pd.DataFrame, strategy: Strategy, config: dict) -> BacktestResult:
    """TODO(ฉาก 2): เริ่มจากเวอร์ชันง่ายสุด (ถือได้ทีละไม้, long อย่างเดียว) ก่อน"""
    raise NotImplementedError
