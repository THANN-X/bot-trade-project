# Architecture

## โครงสร้าง

```
config/default.yaml    ตัวเลขทุกตัว (symbol, ค่าใช้จ่าย, การแบ่งข้อมูล, risk, kill switch)
src/tradebot/
  config.py            โหลด yaml + .env
  data/                ดึงข้อมูล (ccxt) และอ่าน/เขียน CSV
  indicators/          ตัวชี้วัดที่ใช้ร่วมกัน (เช่น ATR) — โค้ดบริสุทธิ์ ห้าม I/O, คำนวณจากข้อมูลเต็มก่อนตัดช่วง
  strategies/          คำนวณสัญญาณ — โค้ดบริสุทธิ์ ห้าม I/O (import indicators/ ได้)
  risk/                ขนาดไม้ + kill switch — ตัดสินว่าทำตามสัญญาณได้ไหม เท่าไหร่
  backtest/            engine, ค่าใช้จ่าย, metrics, journal
  viz/                 กราฟ
  live/                (ฉาก 5) ต่อ exchange จริง/testnet
scripts/               จุดสั่งรัน (fetch_data, run_backtest)
tests/                 pytest
notebooks/             ทดลองเล่น ไม่ใช่โค้ดหลัก
data/                  ข้อมูลดิบ (ไม่เข้า git)
go/                    (ฉาก 4)
docs/                  เอกสาร + journal.jsonl
```

`live/` และ `go/` ยังไม่สร้าง — สร้างเมื่อถึงฉากนั้น

## ทิศทาง import

```
                ┌──────────────┐
                │  strategies  │   ← บริสุทธิ์: DataFrame เข้า → สัญญาณออก
                └──────▲───────┘
                       │ import ได้
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────┴─────┐   ┌────┴────┐    ┌────┴────┐
   │ backtest │   │  risk   │    │  live   │
   └────┬─────┘   └─────────┘    └────┬────┘
        │                             │
   data/ (CSV)                   exchange (ccxt)
```

- `strategies/` import ได้แค่ pandas/numpy, `strategies/base.py` และ `indicators/` — **ห้าม** import `data`, `backtest`, `live`, ccxt, หรืออ่านไฟล์/เวลาปัจจุบัน
- `indicators/` บริสุทธิ์ที่สุด: import ได้แค่ pandas/numpy — ไม่รู้จักแม้แต่ strategy หรือ risk
- `risk/` ก็บริสุทธิ์เช่นกัน: รับตัวเลขเข้า คืนการตัดสินใจออก
- `backtest/` กับ `live/` เป็นคนป้อนข้อมูลให้ strategy และเอาสัญญาณไปทำต่อ

### ทางไปต่อ: hexagonal (ฉาก 5)
โครงตอนนี้เป็นรุ่นง่ายของ hexagonal — strategy บริสุทธิ์แล้ว แต่ยังไม่มี port
ตอนฉาก 5 จะยกขึ้นเป็นเต็มรูปแบบ: ย้าย loop เข้าแกนกลาง, กำหนด port `MarketData` / `Broker`
แล้ว backtest กับ live กลายเป็นแค่ adapter คนละชุด — รายละเอียดและเหตุผลที่รอ:
`docs/decisions/0002-hexagonal-at-stage-5.md`

### ทำไมต้องบริสุทธิ์
ถ้า strategy แอบอ่านไฟล์หรือเรียก exchange เอง พฤติกรรมตอน backtest กับตอนรันจริงจะต่างกันได้โดยไม่รู้ตัว
("backtest สวย แต่ของจริงทำงานคนละแบบ") เมื่อ strategy รู้จักแค่ DataFrame ที่ถูกส่งเข้ามา
โค้ดที่ผ่าน backtest คือโค้ดตัวเดียวกับที่รันจริงแน่นอน — และยังทดสอบ look-ahead อัตโนมัติได้ง่าย
