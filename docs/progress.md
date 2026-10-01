# Progress

Claude อ่านไฟล์นี้ตอนเริ่ม session และอัปเดตทุกครั้งที่จบงาน

## ตอนนี้อยู่: ฉาก 2 — backtest เอง (SMA 20/50)
**ค้างไว้กลางทาง:** —
**ครั้งถัดไป:** `backtest/engine.py` (เริ่มจากถือทีละไม้ long อย่างเดียว)

## ฉาก 0: ปูพื้น
- [x] วางโครงสร้างโปรเจกต์ + เอกสาร (2026-09-25)
- [x] ทบทวนโครงผ่าน + เพิ่มกฎ stop loss กรณี gap และสรุปกฎ backtest ใน CLAUDE.md (2026-09-25)
- [x] ติดตั้ง uv (0.12.19 ผ่าน winget) และรัน `uv sync` ได้ (2026-09-25)
- [x] เข้าใจ OHLCV, ค่าธรรมเนียม, market/limit order — เรียนด้วยข้อมูลจริง + ตอบโจทย์ผ่าน (2026-09-25)
- [x] pandas เบื้องต้น: `notebooks/00_pandas_basics.py` ผ่านครบ 7 ข้อ + ตอบ "คิดดู" (2026-09-26)
  - ข้อสังเกตจากข้อมูลจริง 200 แท่ง: range เฉลี่ย ~477, gap ระหว่างแท่งใหญ่สุด 0.67 USDT
  - พกไปฉาก 2: ฟังก์ชันไม่ควรแก้ df ที่รับเข้ามา (ข้อ 3 แก้ตรง ๆ)
- [x] commit แรก `1cd04cf` (2026-09-25)

## ฉาก 1: ดึงข้อมูล
- [x] `config.load_config` — อ่าน yaml ด้วย utf-8, path อ้างจาก `__file__` ไม่ขึ้นกับ cwd (2026-09-28)
- [x] `data/fetcher.py` — วนดึงทีละหน้า since = แท่งสุดท้าย + 1 แท่ง, ตัดแท่งที่ยังไม่ปิดด้วยเวลาปิดจริง (2 ปี = 18 requests, 2026-09-28)
- [x] `data/storage.py` — เก็บ/อ่าน CSV, round-trip ตรงกัน (index อ่านกลับเป็นหน่วย us แทน ms — ค่าเท่ากัน ไม่กระทบ) (2026-09-28)
- [x] `viz/plot.py` — `plot_price` คืน Figure ไม่ save/show เอง (2026-09-29)
- [x] `scripts/fetch_data.py` รันจบได้ — 17,519 แท่ง 2024-09-29 → 2026-09-29, รันจากโฟลเดอร์อื่นได้ (2026-09-29)
  - ข้อมูลมีทั้งขาขึ้น (~60k→125k), ขาลง (→60k), และฟื้นตัว — ช่วงจูน/ทดสอบ/holdout ตกคนละสภาพตลาด (คุยต่อในฉาก 3)
- [x] ตรวจข้อมูล 2 ปี `notebooks/01_data_check.py` (2026-09-30) — กฎอยู่ที่ backtesting.md §7
  - แท่งหาย: ไม่มี | gap ใหญ่สุด 0.016% (< slippage) | range median 0.5%, max 11.5% (2025-10-10 21:00)
  - stop 300 ใต้ open: 31.5% ของแท่งลงลึกเกิน 300 ภายในแท่งเดียว (ใช้ open−low ไม่ใช่ range)
  - ราคาขึ้น ~21% 19–21 ส.ค. 2026 = ไหลทีละแท่ง + volume ×3–4 ไม่ใช่ gap

## ฉาก 2: backtest เอง (SMA 20/50)
- [x] `strategies/sma_cross.py` — จุดตัดนับเมื่อ SMA ช้ามีค่าทั้งแท่งนี้และแท่งก่อน (กัน BUY ปลอมตอนหมด warm-up); 2 ปี = 194 BUY / 194 SELL (2026-09-30)
- [x] `tests/test_lookahead.py` ผ่าน — ตัดท้าย 3 จุด + ยืนยันว่าข้อมูลปลอมมีสัญญาณ + ไม่แก้ df ที่รับเข้า (2026-09-30)
  - [ ] ลองใส่ `.shift(-1)` ให้ test fail ดูเองหนึ่งครั้ง (ยังไม่ได้ทำ)
- [x] `backtest/costs.py`, `risk/sizing.py` + test 16 ตัว (TDD: test จากตัวเลขในเอกสาร) (2026-09-30)
  - เพดานเงิน = equity ÷ (entry × (1+s) × (1+f)) — แบบคูณ ไม่ใช่บวก (แบบบวกเงินสดติดลบ −0.005)
  - stop 300 ชนเพดาน → เสียจริงเมื่อโดน stop ≈ 0.65% (ราคา 0.35% + ค่าใช้จ่ายไปกลับ ~0.30%)
  - `position_size` คืน `(size, capped)` ให้ engine นับ n_capped — สูตรอยู่ที่ sizing ที่เดียว (2026-10-01)
- [ ] `backtest/engine.py` — รวมกฎ stop loss กรณี open กระโดดข้าม stop และกฎรอยต่อช่วง
- [ ] `backtest/metrics.py` + `tests/test_metrics.py`
- [ ] `backtest/journal.py` — เขียน `docs/journal.jsonl` อัตโนมัติ
- [ ] `scripts/run_backtest.py --split tune` รันจบ + มีบรรทัดใน journal

## ฉาก 3: ตรวจผล + walk-forward + kill switch
- [ ] เทียบผลกับ backtesting.py
- [ ] walk-forward บนช่วงจูน/ทดสอบ
- [ ] stress test: รันซ้ำด้วย slippage 0.2% — ยังต้องกำไร (backtesting.md §2)
- [ ] `max_losing_streak`, `worst_day_pct`
- [ ] เลือกตัวเลข kill switch จากช่วงจูน ใส่ `config/default.yaml`
- [ ] `risk/kill_switch.py`
- [ ] กัน holdout ใน `run_backtest.py` ด้วย `journal.count_runs`
- [ ] รัน holdout ครั้งเดียว
- [ ] ทบทวน decision 0003 (futures) — เริ่มได้เมื่อ expectancy บวกในช่วงทดสอบ + ผ่าน stress test

## ฉาก 4: Go + benchmark
## ฉาก 5: hexagonal + paper trading บน testnet
- [ ] กำหนด port `MarketData`, `Broker` (Protocol)
- [ ] ย้าย loop "อ่านราคา → strategy → risk → ส่งคำสั่ง" เข้าแกนกลาง
- [ ] adapter ชุด backtest: `CsvData` + `SimBroker` — ผล backtest ต้องตรงกับก่อน refactor
- [ ] ตัดสินใจ: สัญญาณเป็นแบบเหตุการณ์หรือสถานะ (ดู 0002) — ถ้าเปลี่ยนต้อง backtest ใหม่
- [ ] กำหนดขนาดหน้าต่างขั้นต่ำของแต่ละกลยุทธ์ (warm-up)
- [ ] test ตัดข้อมูลส่วนหัว: หลังพ้น warm-up สัญญาณต้องตรงกับข้อมูลเต็ม
- [ ] adapter ชุด live: `ExchangeData` (WebSocket) + `ExchangeBroker` (ccxt testnet)
- [ ] stop loss แบบ stop-market (ห้าม stop-limit) — ถ้า exchange ไม่รองรับ ตัดสินใจว่าจะให้บอทเฝ้าราคาเองแล้วส่ง market order ไหม (backtesting.md หัวข้อ 6)
- [ ] วัด slippage จริง แยกไม้ปกติกับไม้ที่ออกด้วย stop (โดยเฉพาะช่วงข่าวแรง) แล้วปรับ `costs.slippage_pct`
- [ ] เปิดกฎกันบอทพัง (ราคาค้าง, สั่งถี่, สถานะใหญ่เกิน)
- [ ] paper trade 1–3 เดือน
