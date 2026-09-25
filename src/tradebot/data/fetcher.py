"""ดึงข้อมูลแท่งเทียน (OHLCV) จาก exchange ผ่าน ccxt

ผลลัพธ์: DataFrame คอลัมน์ timestamp (UTC), open, high, low, close, volume
เรียงจากเก่าไปใหม่ ไม่มีแถวซ้ำ
"""

import pandas as pd


def fetch_ohlcv(exchange: str, symbol: str, timeframe: str, days: int) -> pd.DataFrame:
    """ดึงข้อมูลย้อนหลัง `days` วัน

    TODO(ฉาก 1):
    - exchange ส่งข้อมูลได้ครั้งละจำกัด (เช่น 1000 แท่ง) ต้องวนดึงเป็นหน้า ๆ
    - แปลง timestamp (milliseconds) เป็น datetime UTC
    - ตัดแถวซ้ำตรงรอยต่อระหว่างหน้า
    - timestamp ของ ccxt = เวลา "เปิด" แท่ง → แท่งสุดท้ายมักยังไม่ปิด ต้องตัดทิ้ง
      (ดู docs/backtesting.md หัวข้อ 1 — จะรู้ได้ยังไงว่าแท่งไหนปิดแล้ว?)
    """
    raise NotImplementedError
