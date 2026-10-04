"""บันทึกผล backtest ลง docs/journal.jsonl อัตโนมัติทุกครั้งที่รัน

ทำไมอัตโนมัติ: ถ้าต้องจดเอง สักวันจะลืมจดรอบที่ผลไม่สวย ซึ่งเป็นรอบที่สำคัญที่สุด
รูปแบบแต่ละบรรทัด: docs/backtesting.md หัวข้อ 4

JSONL = หนึ่งบรรทัดหนึ่ง JSON เขียนต่อท้ายได้เรื่อย ๆ โดยไม่ต้องอ่านทั้งไฟล์
ห้ามแก้หรือลบบรรทัดเก่า
"""

import json
import math
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from tradebot.config import PROJECT_ROOT

JOURNAL_PATH = PROJECT_ROOT / "docs" / "journal.jsonl"


def git_info(repo: Path = PROJECT_ROOT) -> dict:
    """คืน {"git_commit": ..., "git_dirty": ...} — ใช้ย้อนกลับไปหาโค้ดที่สร้างผลแต่ละรอบ

      git rev-parse --short HEAD   → commit hash (ยังไม่เคย commit → error → None)
      git status --porcelain       → มีข้อความ = dirty (มีโค้ดที่ยังไม่ commit ตอนรัน)

    repo — โฟลเดอร์ของ repo ค่าเริ่มต้น = โปรเจกต์นี้ (test ส่ง repo ปลอมเข้ามา)
    """
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )

    if head.returncode == 0:  # commit hash
        commit = head.stdout.strip()
    else:
        commit = None

    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=repo, capture_output=True, text=True, check=False
    )

    if status.returncode == 0:
        dirty = bool(status.stdout.strip())
    else:
        dirty = False

    return {"git_commit": commit, "git_dirty": dirty}


def _json_safe(value):
    """แปลงค่าที่ JSON มาตรฐานเขียนไม่ได้ ทุกชั้นของ dict ที่ซ้อนกัน

    - ตัวเลขของ numpy (int64, float64, bool) → ตัวเลขของ Python (.item())
    - inf → None
    เรียกตัวเองซ้ำ (recursion) กับค่าที่เป็น dict จึงจัดการ results ที่ซ้อนอยู่ข้างในได้
    NaN ไม่แปลง — ปล่อยให้ json.dumps(allow_nan=False) error เพราะ NaN แปลว่ามีบั๊ก
    """
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and math.isinf(value):
        return None
    return value


def append_entry(entry: dict, path: Path = JOURNAL_PATH) -> None:
    """เติม run_at (UTC) + git_info แล้วเขียนต่อท้ายไฟล์หนึ่งบรรทัด

    กติกาค่าพิเศษ (docs/backtesting.md หัวข้อ 4):
      - float("inf") → None (เขียนเป็น null) — profit_factor ที่ไม่มีไม้แพ้
      - NaN → ValueError และไม่เขียนอะไรลงไฟล์ (แปลว่ามีบั๊กใน metrics)

    ไม่แก้ entry ที่คนเรียกส่งมา — สร้าง dict ใหม่
    ลำดับ: เตรียมข้อความให้เสร็จก่อน แล้วค่อยเปิดไฟล์ → ถ้า error จะไม่มีบรรทัดครึ่ง ๆ ค้างในไฟล์
    """
    record = {
        "run_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **git_info(),
        **entry,
    }
    line = json.dumps(_json_safe(record), ensure_ascii=False, allow_nan=False)

    with open(path, "a", encoding="utf-8") as file:
        file.write(line + "\n")


def count_runs(strategy: str, split: str, path: Path = JOURNAL_PATH) -> int:
    """นับว่ารันกลยุทธ์นี้บนช่วงข้อมูลนี้ไปกี่ครั้งแล้ว

    ใช้ตรวจ: holdout ถูกแตะไปแล้วหรือยัง, ลองพารามิเตอร์ไปกี่ชุด (overfitting)

    TODO(ฉาก 3)
    """
    raise NotImplementedError
