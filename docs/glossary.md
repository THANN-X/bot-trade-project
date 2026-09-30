# Glossary

ความหมาย **ในโปรเจกต์นี้** — เฉพาะคำที่ผูกกับการตัดสินใจของโปรเจกต์ ไม่ใช่นิยามทั่วไป
Claude ดูแลไฟล์นี้: เมื่อกฎในเอกสารอื่นเปลี่ยน ต้องแก้ที่นี่ให้ตรง (กฎจริงอยู่ที่ลิงก์ในคอลัมน์ขวา)

## ข้อมูลและเวลา
| คำ | ในโปรเจกต์นี้ | ที่มา |
|---|---|---|
| OHLCV / แท่ง | timestamp = เวลา **เปิด** แท่ง, UTC; แท่งที่ยังไม่ปิดตัดทิ้งก่อนเก็บ | backtesting.md §1 |
| วัน | เริ่มนับใหม่ 00:00 UTC (ใช้กับขาดทุนต่อวัน, worst day) | decisions/0001 |
| Warm-up | จำนวนแท่งที่ indicator ต้องใช้ก่อนให้ค่าที่เชื่อได้ — SMA cross 20/50 ≥ 51 แท่ง | decisions/0002 |

## สัญญาณและคำสั่ง
| คำ | ในโปรเจกต์นี้ | ที่มา |
|---|---|---|
| สัญญาณ | แบบ **เหตุการณ์**: BUY/SELL เฉพาะแท่งที่เส้นตัดกัน; แบบสถานะตัดสินที่ฉาก 5 | decisions/0002 |
| เข้าไม้ | market order ที่ **open ของแท่งถัดไป** หลังสัญญาณ + slippage + fee | backtesting.md §1, §2 |
| Market order | ทุกคำสั่งใน backtest: เข้า, ออกด้วย SELL, stop, ปิดที่รอยต่อช่วง | backtesting.md §2 |
| Limit order | **ไม่ใช้** ใน backtest — จำลองว่าได้ของหรือไม่ได้ยาก | backtesting.md §2 |
| Stop loss | = **stop-market** ทั้ง backtest และ live ห้าม stop-limit; open ข้าม stop → ปิดที่ open | backtesting.md §6 |
| Maker / taker | ไม่แยก — คิดทุกคำสั่งเป็น taker 0.1% | backtesting.md §2 |

## ค่าใช้จ่าย
| คำ | ในโปรเจกต์นี้ | ที่มา |
|---|---|---|
| Fee | 0.1% ต่อข้าง คิดจากราคาหลังหัก slippage | backtesting.md §2, §6 |
| Slippage | 0.05% ต่อข้าง ทุกคำสั่ง (ซื้อแพงขึ้น, ขายถูกลง); วัดจริงในฉาก 5 แยกไม้ stop | backtesting.md §2, §6 |
| Spread | ไม่คิดแยก — รวมอยู่ใน slippage (ใช้ได้กับ BTC/USDT; เปลี่ยนคู่ต้องวัดก่อน) | backtesting.md §2 |

## ความเสี่ยง
| คำ | ในโปรเจกต์นี้ | ที่มา |
|---|---|---|
| ความเสี่ยงต่อไม้ | 1% ของพอร์ต (เพดาน 2%); ขนาดไม้ = เงินที่ยอมเสีย ÷ ระยะ stop | risk/sizing.py |
| เพดานเงิน | ขนาดไม้ไม่เกิน equity ÷ (entry × (1+slippage) × (1+fee)) — spot ไม่มี leverage; ถูกตัดแล้วเทรดต่อ (≠ `max_position_pct` ที่หยุดบอท) | backtesting.md §2 |
| Drawdown | ลดจากจุดสูงสุดของ equity; เกิน 15% → หยุดถาวร ต้อง backtest ใหม่ | decisions/0001 |
| Kill switch | กฎหยุดบอท 4 ข้อ ตัวเลขมาจาก backtest ช่วงจูน | decisions/0001 |
| Cool-off | แก้กลยุทธ์ได้หลังผ่านไป ≥ 1 เดือน และต้อง backtest ใหม่ | CLAUDE.md |

## การวัดผลและการแบ่งข้อมูล
| คำ | ในโปรเจกต์นี้ | ที่มา |
|---|---|---|
| Expectancy | กำไรสุทธิ **หลังหักค่าใช้จ่าย** ÷ จำนวนไม้ — ต้องเป็นบวก | CLAUDE.md |
| Profit factor | กำไรรวมไม้ชนะ ÷ ขาดทุนรวมไม้แพ้ — ต่ำกว่า 1 = เสียเงิน | CLAUDE.md |
| Win rate | ใช้ประกอบเท่านั้น ไม่ใช่ตัวตัดสิน | CLAUDE.md |
| Look-ahead bias | ใช้ข้อมูลอนาคตโดยไม่รู้ตัว — `test_lookahead.py` ต้องผ่านทุกกลยุทธ์ | backtesting.md §1 |
| จูน / ทดสอบ / holdout | 60 / 20 / 20 ตามเวลา; holdout แตะได้ครั้งเดียว; ทุกช่วงเริ่มพอร์ตว่าง | backtesting.md §3 |
| Journal | `docs/journal.jsonl` บันทึกทุกการรันอัตโนมัติ ห้ามแก้บรรทัดเก่า | backtesting.md §4 |

## โครงสร้าง
| คำ | ในโปรเจกต์นี้ | ที่มา |
|---|---|---|
| Hexagonal / port / adapter | รอฉาก 5 — port `MarketData` / `Broker`; backtest กับ live เป็น adapter คนละชุด | decisions/0002 |
