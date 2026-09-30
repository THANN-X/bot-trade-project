"""ฉาก 1 — ตรวจข้อมูล 2 ปีก่อนเอาไปใช้ backtest

รัน: uv run python notebooks/01_data_check.py
(ต้องรัน scripts/fetch_data.py ก่อน ให้มีไฟล์ CSV)

ต่างจาก 00_pandas_basics ตรงที่ไม่มีเฉลย — เรากำลังหาสิ่งที่ยังไม่รู้เกี่ยวกับข้อมูล
ถ้าเจออะไรผิดปกติ ตัดสินใจว่าจะจัดการยังไง แล้วจดลง docs/backtesting.md
"""

import sys

import pandas as pd

from tradebot.config import PROJECT_ROOT
from tradebot.data.storage import load_csv

CSV = PROJECT_ROOT / "data" / "raw" / "binance_BTC-USDT_1h.csv"


# ── 1. แท่งหาย ─────────────────────────────────────────────────────────────
def missing_bars(df: pd.DataFrame) -> pd.Series:
    """คืนเฉพาะจุดที่แถวติดกันห่างกันไม่ใช่ 1 ชม. พอดี
    index = เวลาของแถวที่อยู่หลังรู, ค่า = ระยะห่างจากแถวก่อนหน้า (Timedelta)

    คำใบ้: index ยังไม่ใช่ Series → .to_series() ก่อน แล้วใช้ .diff()
           (diff = ค่าแถวนี้ − ค่าแถวก่อนหน้า — คิดดูว่าต่างจาก shift ยังไง)
           เทียบกับ pd.Timedelta("1h") แล้วกรองแบบ ex4
    คิดดู: แถวแรกได้ค่าอะไร ควรนับว่าเป็น "แท่งหาย" ไหม
    """
    timedelta_diff = df.index.to_series().diff().dropna(axis=0)
    missing_bars = timedelta_diff[timedelta_diff != pd.Timedelta("1h")]
    return missing_bars


# ── 2. gap ระหว่างแท่ง ─────────────────────────────────────────────────────
def largest_gaps(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """คืน n แถวที่ |open − close ก่อนหน้า| ใหญ่ที่สุด
    คอลัมน์: prev_close, open, gap, gap_pct (gap ÷ prev_close)

    คำใบ้: ต่อยอดจาก ex6; .abs(); .nlargest(n, "ชื่อคอลัมน์") หรือ sort_values
    คิดดู: gap ใหญ่สุดใน 2 ปียังเล็กเหมือนช่วง 8 วัน (0.67 USDT) ไหม
           ถ้าไม่ — ตรงกับจุดที่ข้อ 1 เจอแท่งหายหรือเปล่า
    """
    prev_close = df["close"].shift(1)
    gap = (df["open"] - prev_close).abs()
    gap_pct = gap / prev_close

    df = pd.DataFrame({
        "prev_close": prev_close,
        "open": df["open"],
        "gap": gap,
        "gap_pct": gap_pct
    })

    stats = df.nlargest(n, "gap_pct")
    
    return stats


# ── 3. range ────────────────────────────────────────────────────────────────
def range_stats(df: pd.DataFrame, n: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """คืน (สถิติของ range, n แท่งที่ range กว้างที่สุด)
    range ให้คิดเป็น % ของ open ด้วย (range_pct) — ราคา 60k กับ 120k แกว่ง 500 ไม่เท่ากัน

    คำใบ้: .describe() ให้ count/mean/std/min/25%/50%/75%/max ในคำสั่งเดียว
    คิดดู: mean กับ 50% (median) ต่างกันแค่ไหน บอกอะไรเรื่องแท่งที่แกว่งผิดปกติ
           stop ห่าง 300 จากฉาก 0 อยู่ตรงไหนของการกระจายนี้
    """
    rng = df["high"] - df["low"]
    rng_pct = rng / df["open"]
    drop_from_open = df["open"] - df["low"]
    df = pd.DataFrame({
        "range": rng,
        "range_pct": rng_pct,
        "open": df["open"],
        "high": df["high"],
        "low": df["low"],
        "drop_from_open": drop_from_open})
    stats = df[["range", "range_pct", "drop_from_open"]].describe()
    largest_ranges = df.nlargest(n, "range_pct")
    return stats, largest_ranges

# ── 4. ส่องช่วงราคากระโดด ~20 ส.ค. 2026 ───────────────────────────────────
def zoom(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """คืนข้อมูลช่วง start ถึง end แปลงเป็นแท่งรายวัน (1D) พร้อมคอลัมน์ change_pct

    คำใบ้: df.loc["2026-08-15":"2026-08-25"] เลือกช่วงเวลาได้ตรง ๆ;
           resample แบบ ex7 แต่ใช้ "1D"; change_pct = close ÷ open − 1
    คิดดู: ราคากระโดดทีเดียวในแท่งเดียว (gap) หรือค่อย ๆ ขึ้นหลายแท่ง
           ถ้าเกิดแบบเดียวกันในทิศลงตอนเราถือ long อยู่ กฎ stop หัวข้อ 6 ข้อไหนจะทำงาน
    """

    window = df.loc[start:end]  # เลือกช่วงเวลา
    daily_df = window.resample("1D").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })
    daily_df["change_pct"] = daily_df["close"] / daily_df["open"] - 1

    return daily_df


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", None)  # ไม่ย่อคอลัมน์เป็น "..."
    df = load_csv(CSV)
    print(f"{len(df)} แท่ง: {df.index[0]} → {df.index[-1]}\n")

    for title, fn, args in [
        ("1. แท่งหาย", missing_bars, (df,)),
        ("2. gap ใหญ่สุด", largest_gaps, (df,)),
        ("3. range", range_stats, (df,)),
        ("4. ส่องช่วง 15–25 ส.ค. 2026", zoom, (df, "2026-08-15", "2026-08-25")),
    ]:
        print(f"━━━ {title}")
        try:
            out = fn(*args)
        except NotImplementedError:
            print("ยังไม่ทำ\n")
            continue
        for part in out if isinstance(out, tuple) else (out,):
            print(part if len(part) else "(ไม่มี)")
        print()


if __name__ == "__main__":
    main()
