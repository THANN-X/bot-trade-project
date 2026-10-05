"""ATR (Average True Range) — ระยะแกว่งเฉลี่ยต่อแท่ง ใช้ตั้ง stop ตามความผันผวน (stop_method: atr)

True Range ของแท่ง = ค่าที่มากที่สุดของ
  high − low                  (แกว่งภายในแท่ง)
  |high − close แท่งก่อน|      (รวม gap ขึ้น)
  |low − close แท่งก่อน|       (รวม gap ลง)
แท่งแรกไม่มี close ก่อนหน้า → True Range = NaN

ATR(N) = ค่าเฉลี่ยธรรมดาของ True Range N แท่งล่าสุด → warm-up N + 1 แท่ง (N = 14 → 15 แท่ง)

หมายเหตุ: ค่าจะต่างจาก ATR บน TradingView เล็กน้อย เพราะ TradingView ใช้สูตร Wilder
(ค่าเฉลี่ยถ่วงน้ำหนัก α = 1/N ที่จำอดีตทั้งหมด) — เราเลือกค่าเฉลี่ยธรรมดาเพราะตรวจมือได้
และค่าตรงเป๊ะทั้ง backtest และ live เมื่อมีข้อมูลครบ N + 1 แท่ง (decision 0002 ตาราง warm-up)
"""

import pandas as pd


def atr(df: pd.DataFrame, period: int) -> pd.Series:
    """คืน ATR ทุกแท่ง (index เดียวกับ df) — period แท่งแรกเป็น NaN

    ห้ามแก้ df ที่รับเข้ามา และห้ามใช้ข้อมูลอนาคต (tests/test_atr.py ตรวจทั้งสองเรื่อง)

    skipna=False: แท่งแรกไม่มี close ก่อนหน้า สองตัวหลังเป็น NaN — ถ้าปล่อยให้ max ข้าม NaN
    จะได้ high − low แทน แล้ว ATR ตัวแรกออกเร็วไป 1 แท่ง (warm-up ต้องเป็น N + 1)
    """
    previous_close = df["close"].shift(1)
    true_range = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - previous_close).abs(),
            (df["low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1, skipna=False)

    atr_series = true_range.rolling(window=period).mean()

    return atr_series
