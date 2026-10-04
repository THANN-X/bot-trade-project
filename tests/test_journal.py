"""journal — เขียนผล backtest ต่อท้าย docs/journal.jsonl (กติกาอยู่ที่ docs/backtesting.md หัวข้อ 4)

ทุก test เขียนลงไฟล์ชั่วคราว (fixture tmp_path ของ pytest) ไม่แตะ docs/journal.jsonl ตัวจริง
เพราะไฟล์นั้นต้องมีเฉพาะผลการรันจริง และห้ามแก้บรรทัดเก่า

ข้อตกลงที่ test กำหนด:
- run_at = เวลา UTC แบบ "2026-10-01T08:30:00Z" (ตามตัวอย่างในเอกสาร)
- git_info(repo) รับโฟลเดอร์ของ repo ได้ (ค่าเริ่มต้น = PROJECT_ROOT) เพื่อให้ test สร้าง repo ปลอมได้
- ยังไม่เคย commit → git_commit = None (ไม่ error)
- append_entry ไม่แก้ dict ที่คนเรียกส่งมา
"""

import json
import math
import subprocess
from datetime import UTC, datetime

import pytest

from tradebot.backtest.journal import append_entry, git_info


def read_lines(path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def git(repo, *args: str) -> None:
    """รันคำสั่ง git ใน repo ปลอม — ตั้งชื่อผู้ commit ไว้ในคำสั่ง จะได้ไม่พึ่ง config ของเครื่อง"""
    subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@example.com", *args],
        cwd=repo,
        check=True,
        capture_output=True,
    )


# ── append_entry: เขียนต่อท้าย ───────────────────────────────────────────────
def test_appends_one_line_per_call(tmp_path):
    """รัน 2 ครั้ง = 2 บรรทัด — ต่อท้าย ไม่เขียนทับ"""
    path = tmp_path / "journal.jsonl"

    append_entry({"strategy": "a"}, path)
    append_entry({"strategy": "b"}, path)

    lines = read_lines(path)
    assert [e["strategy"] for e in lines] == ["a", "b"]


def test_adds_run_at_in_utc(tmp_path):
    path = tmp_path / "journal.jsonl"
    before = datetime.now(UTC).replace(microsecond=0)

    append_entry({"strategy": "a"}, path)

    run_at = read_lines(path)[0]["run_at"]
    assert run_at.endswith("Z")
    parsed = datetime.strptime(run_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    assert parsed >= before


def test_adds_git_info(tmp_path):
    """ทุกบรรทัดต้องย้อนกลับไปหาโค้ดที่รันได้ (backtesting.md หัวข้อ 4)"""
    path = tmp_path / "journal.jsonl"

    append_entry({"strategy": "a"}, path)

    entry = read_lines(path)[0]
    assert "git_commit" in entry
    assert isinstance(entry["git_dirty"], bool)


def test_does_not_modify_callers_dict(tmp_path):
    entry = {"strategy": "a", "results": {"n_trades": 3}}

    append_entry(entry, tmp_path / "journal.jsonl")

    assert entry == {"strategy": "a", "results": {"n_trades": 3}}


def test_thai_text_stays_readable(tmp_path):
    """ensure_ascii=False + เขียนด้วย UTF-8 — ไม่กลายเป็น \\u0e17\\u0e14..."""
    path = tmp_path / "journal.jsonl"

    append_entry({"note": "ทดสอบ"}, path)

    assert "ทดสอบ" in path.read_text(encoding="utf-8")


# ── ค่าพิเศษ (backtesting.md หัวข้อ 4) ──────────────────────────────────────
def test_infinite_profit_factor_becomes_null(tmp_path):
    """ไม่มีไม้แพ้ → metrics คืน inf → journal เขียน null (ค่าที่ซ้อนอยู่ใน results ก็ต้องแปลง)"""
    path = tmp_path / "journal.jsonl"

    append_entry({"results": {"profit_factor": math.inf, "n_trades": 5}}, path)

    results = read_lines(path)[0]["results"]
    assert results["profit_factor"] is None
    assert results["n_trades"] == 5


def test_nan_is_rejected_and_nothing_is_written(tmp_path):
    """NaN แปลว่ามีบั๊ก → error ทันที และต้องไม่มีบรรทัดครึ่ง ๆ กลาง ๆ ค้างในไฟล์"""
    path = tmp_path / "journal.jsonl"
    append_entry({"strategy": "ok"}, path)

    with pytest.raises(ValueError):
        append_entry({"results": {"expectancy": math.nan}}, path)

    assert len(read_lines(path)) == 1


# ── git_info ──────────────────────────────────────────────────────────────────
def test_git_info_before_first_commit(tmp_path):
    """repo ใหม่ยังไม่มี commit → git rev-parse error → คืน None ไม่ใช่พัง"""
    git(tmp_path, "init")

    info = git_info(tmp_path)

    assert info["git_commit"] is None


def test_git_info_clean_then_dirty(tmp_path):
    git(tmp_path, "init")
    (tmp_path / "a.txt").write_text("1", encoding="utf-8")
    git(tmp_path, "add", "a.txt")
    git(tmp_path, "commit", "-m", "first")

    clean = git_info(tmp_path)
    assert len(clean["git_commit"]) >= 7
    assert clean["git_dirty"] is False

    (tmp_path / "a.txt").write_text("2", encoding="utf-8")  # แก้ไฟล์แต่ยังไม่ commit
    assert git_info(tmp_path)["git_dirty"] is True


def test_git_info_matches_this_repo():
    """ค่าเริ่มต้นต้องอ่านจาก repo ของโปรเจกต์นี้"""
    expected = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    assert git_info()["git_commit"] == expected
