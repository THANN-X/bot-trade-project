# tradebot

บอทวิเคราะห์และเทรดแบบมีระบบ — ฝึกบนคริปโต (BTC/USDT) ด้วยข้อมูลย้อนหลังและ testnet เท่านั้น

## ติดตั้ง

ต้องมี [uv](https://docs.astral.sh/uv/)

```bash
uv sync
cp .env.example .env   # ยังไม่ต้องใส่ค่าจนถึงฉาก 5
```

## รัน

```bash
uv run python scripts/fetch_data.py     # ดึงข้อมูล
uv run python scripts/run_backtest.py   # backtest
uv run pytest                           # ทดสอบ
uv run ruff check .                     # ตรวจโค้ด
```

## เอกสาร

- `CLAUDE.md` — เป้าหมาย, roadmap, กฎทั้งหมด
- `docs/progress.md` — ตอนนี้อยู่ตรงไหน
- `docs/architecture.md` — โครงสร้างและทิศทาง import
- `docs/backtesting.md` — กฎกัน bias, ค่าใช้จ่าย, การแบ่งข้อมูล
- `docs/journal.jsonl` — ผล backtest ทุกครั้ง (เขียนอัตโนมัติ)
- `docs/decisions/` — เหตุผลของการตัดสินใจสำคัญ
