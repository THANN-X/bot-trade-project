"""รัน backtest ตาม config แล้วพิมพ์ metrics + บันทึกลง docs/journal.jsonl อัตโนมัติ

รัน:
  uv run python scripts/run_backtest.py --split tune
  uv run python scripts/run_backtest.py --split test
  uv run python scripts/run_backtest.py --split holdout   # ครั้งเดียวเท่านั้น

TODO(ฉาก 2): load_config → load_csv → SmaCross.generate_signals(ข้อมูลเต็ม)
            → ตัดทั้งราคาและสัญญาณตาม split → run_backtest
            → คำนวณ metrics → พิมพ์ → journal.append_entry (ทุกครั้ง ไม่มีข้อยกเว้น)
  - คำนวณสัญญาณจากข้อมูลเต็มก่อนตัด (กัน warm-up และจุดตัดคาบรอยต่อหาย)
  - กฎรอยต่อช่วง (docs/backtesting.md หัวข้อ 3): พอร์ตว่างตอนเริ่ม, ปิดไม้ค้างที่ close
    ของแท่งสุดท้าย, ไม่ใช้สัญญาณแท่งสุดท้าย — engine เป็นคนทำ แต่ตรวจว่าส่งข้อมูลถูกช่วง
TODO(ฉาก 3): ถ้า --split holdout และ journal.count_runs(...) > 0 ให้หยุดพร้อมคำเตือน
"""


def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
