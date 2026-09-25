"""Kill switch — หยุดบอทตามกฎที่เขียนไว้ล่วงหน้า ไม่ใช่ตามอารมณ์

ตัวเลขทุกตัวมาจาก config (kill_switch:) ซึ่งเลือกจาก backtest
เหตุผล: docs/decisions/0001-kill-switch-from-backtest.md

กลุ่ม A (กันกลยุทธ์แย่) — แต่ละกฎหยุดหนักเบาต่างกัน:
  daily_loss    → PAUSE_UNTIL_NEXT_DAY   กลับมาเองเมื่อข้ามเที่ยงคืน UTC
  losing_streak → HALT_UNTIL_REVIEW      รอคนตรวจแล้วสั่งเปิด
  max_drawdown  → HALT_UNTIL_REBACKTEST  หยุดถาวร ต้อง backtest ใหม่

กลุ่ม B (กันบอทพัง) — ใช้ตอน paper/live จะเพิ่มในฉาก 5
"""

from enum import Enum


class Action(Enum):
    CONTINUE = "continue"
    PAUSE_UNTIL_NEXT_DAY = "pause_until_next_day"
    HALT_UNTIL_REVIEW = "halt_until_review"
    HALT_UNTIL_REBACKTEST = "halt_until_rebacktest"


class KillSwitch:
    def __init__(self, config: dict):
        """รับ config["kill_switch"]

        TODO(ฉาก 3): ถ้าค่าไหนยังเป็น null ให้ถือว่ากฎนั้นปิดอยู่ใน backtest
        แต่ตอน paper/live ต้อง error ทันที — ห้ามรันโดยยังไม่ได้เลือกตัวเลข
        """
        self.config = config

    def on_trade_closed(self, pnl: float, equity: float, timestamp) -> Action:
        """เรียกทุกครั้งที่ปิดไม้ อัปเดตตัวนับแล้วคืน Action ที่หนักที่สุดที่ชน

        TODO(ฉาก 3):
        - นับแพ้ติดกัน (ชนะ 1 ไม้ = รีเซ็ต)
        - สะสมขาดทุนของวัน (รีเซ็ตเมื่อข้าม day_reset_utc)
        - ติดตาม equity สูงสุด เพื่อคำนวณ drawdown
        """
        raise NotImplementedError
