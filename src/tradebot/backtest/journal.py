"""บันทึกผล backtest ลง docs/journal.jsonl อัตโนมัติทุกครั้งที่รัน

ทำไมอัตโนมัติ: ถ้าต้องจดเอง สักวันจะลืมจดรอบที่ผลไม่สวย ซึ่งเป็นรอบที่สำคัญที่สุด
รูปแบบแต่ละบรรทัด: docs/backtesting.md หัวข้อ 4

JSONL = หนึ่งบรรทัดหนึ่ง JSON เขียนต่อท้ายได้เรื่อย ๆ โดยไม่ต้องอ่านทั้งไฟล์
ห้ามแก้หรือลบบรรทัดเก่า
"""

from pathlib import Path

from tradebot.config import PROJECT_ROOT

JOURNAL_PATH = PROJECT_ROOT / "docs" / "journal.jsonl"


def git_info() -> dict:
    """คืน {"git_commit": ..., "git_dirty": ...}

    TODO(ฉาก 2): ใช้ subprocess เรียก
      git rev-parse --short HEAD        → commit hash
      git status --porcelain            → มีผลลัพธ์ = dirty
    ถ้ายังไม่เคย commit เลย คำสั่งแรกจะ error — จะคืนค่าอะไร?
    """
    raise NotImplementedError


def append_entry(entry: dict, path: Path = JOURNAL_PATH) -> None:
    """เติม run_at (UTC) + git_info แล้วเขียนต่อท้ายไฟล์หนึ่งบรรทัด

    TODO(ฉาก 2): เปิดไฟล์โหมด "a" และใช้ json.dumps(..., ensure_ascii=False)
    """
    raise NotImplementedError


def count_runs(strategy: str, split: str, path: Path = JOURNAL_PATH) -> int:
    """นับว่ารันกลยุทธ์นี้บนช่วงข้อมูลนี้ไปกี่ครั้งแล้ว

    ใช้ตรวจ: holdout ถูกแตะไปแล้วหรือยัง, ลองพารามิเตอร์ไปกี่ชุด (overfitting)

    TODO(ฉาก 3)
    """
    raise NotImplementedError
