"""Backtest engine — เดินทีละแท่ง จำลองการเข้า/ออกออเดอร์

แบบผสม (docs/backtesting.md หัวข้อ 5): สัญญาณคำนวณทั้งตารางก่อนครั้งเดียว
ด้วย strategy.generate_signals(df) แล้ว loop นี้ทำแค่การเข้า/ออกไม้

ลำดับต่อแท่ง:
  1. อ่านสัญญาณของแท่งก่อนหน้า (ที่ปิดแล้ว)
  2. ถ้ามีสัญญาณ → ถาม risk/ ว่าเข้าได้ไหม ขนาดเท่าไหร่
  3. เข้าออเดอร์ที่ open ของแท่งนี้ + หักค่าธรรมเนียม/slippage (costs.py)
  4. เช็ค stop loss ด้วย high/low ของแท่งนี้
  5. แจ้ง kill switch เมื่อปิดไม้

พฤติกรรมที่ตั้งใจ (สัญญาณแบบเหตุการณ์ — ดู docs/decisions/0002):
  - โดน stop loss แล้ว → ถือเงินสด รอ BUY ครั้งถัดไป ไม่กลับเข้าทันที
    แม้ SMA20 ยังอยู่เหนือ SMA50 ก็ตาม
  - ได้ SELL ตอนไม่มีไม้ → ไม่ทำอะไร (เช่น หลังโดน stop แล้วเส้นค่อยตัดลง)

กฎรอยต่อช่วงข้อมูล (docs/backtesting.md หัวข้อ 3):
  - เริ่มด้วยพอร์ตว่างเสมอ (เงินสด = initial_capital ไม่มีไม้ค้าง)
  - ยังถือไม้ตอนแท่งสุดท้าย → ปิดที่ close ของแท่งนั้น หักค่าธรรมเนียม/slippage
  - ไม่ใช้สัญญาณของแท่งสุดท้าย (จะเข้าไม้ที่ open ของแท่งถัดไปซึ่งอยู่นอกช่วง)
  - engine รับสัญญาณที่คำนวณจากข้อมูลเต็มมาแล้ว ไม่คำนวณใหม่จากข้อมูลที่ตัดแล้ว
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
