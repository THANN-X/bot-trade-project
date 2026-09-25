# Progress

Claude อ่านไฟล์นี้ตอนเริ่ม session และอัปเดตทุกครั้งที่จบงาน

## ตอนนี้อยู่: ฉาก 0 — ปูพื้น
**ค้างไว้กลางทาง:** —
**ครั้งถัดไป:** ติดตั้ง uv → `uv sync` → เริ่มเรียน OHLCV

## ฉาก 0: ปูพื้น
- [x] วางโครงสร้างโปรเจกต์ + เอกสาร (2026-09-25)
- [ ] ติดตั้ง uv และรัน `uv sync` ได้
- [ ] เข้าใจ OHLCV, ค่าธรรมเนียม, market/limit order (จด `docs/glossary.md`)
- [ ] ลอง pandas เบื้องต้นใน `notebooks/`
- [ ] commit แรก (journal ต้องใช้ git hash)

## ฉาก 1: ดึงข้อมูล
- [ ] `config.load_config`
- [ ] `data/fetcher.py` — วนดึง BTC/USDT 1h ย้อนหลัง 2 ปี, ตัดแท่งที่ยังไม่ปิด
- [ ] `data/storage.py` — เก็บ/อ่าน CSV
- [ ] `viz/plot.py` — กราฟราคา
- [ ] `scripts/fetch_data.py` รันจบได้

## ฉาก 2: backtest เอง (SMA 20/50)
- [ ] `strategies/sma_cross.py`
- [ ] `tests/test_lookahead.py` ผ่าน (และลองทำให้ fail ด้วย `.shift(-1)` ดูหนึ่งครั้ง)
- [ ] `backtest/costs.py`, `risk/sizing.py`
- [ ] `backtest/engine.py`
- [ ] `backtest/metrics.py` + `tests/test_metrics.py`
- [ ] `backtest/journal.py` — เขียน `docs/journal.jsonl` อัตโนมัติ
- [ ] `scripts/run_backtest.py --split tune` รันจบ + มีบรรทัดใน journal

## ฉาก 3: ตรวจผล + walk-forward + kill switch
- [ ] เทียบผลกับ backtesting.py
- [ ] walk-forward บนช่วงจูน/ทดสอบ
- [ ] `max_losing_streak`, `worst_day_pct`
- [ ] เลือกตัวเลข kill switch จากช่วงจูน ใส่ `config/default.yaml`
- [ ] `risk/kill_switch.py`
- [ ] กัน holdout ใน `run_backtest.py` ด้วย `journal.count_runs`
- [ ] รัน holdout ครั้งเดียว

## ฉาก 4: Go + benchmark
## ฉาก 5: hexagonal + paper trading บน testnet
- [ ] กำหนด port `MarketData`, `Broker` (Protocol)
- [ ] ย้าย loop "อ่านราคา → strategy → risk → ส่งคำสั่ง" เข้าแกนกลาง
- [ ] adapter ชุด backtest: `CsvData` + `SimBroker` — ผล backtest ต้องตรงกับก่อน refactor
- [ ] ตัดสินใจ: สัญญาณเป็นแบบเหตุการณ์หรือสถานะ (ดู 0002) — ถ้าเปลี่ยนต้อง backtest ใหม่
- [ ] กำหนดขนาดหน้าต่างขั้นต่ำของแต่ละกลยุทธ์ (warm-up)
- [ ] test ตัดข้อมูลส่วนหัว: หลังพ้น warm-up สัญญาณต้องตรงกับข้อมูลเต็ม
- [ ] adapter ชุด live: `ExchangeData` (WebSocket) + `ExchangeBroker` (ccxt testnet)
- [ ] เปิดกฎกันบอทพัง (ราคาค้าง, สั่งถี่, สถานะใหญ่เกิน)
- [ ] paper trade 1–3 เดือน
