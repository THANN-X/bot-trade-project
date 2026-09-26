"""ฉาก 0 — pandas เบื้องต้น ด้วยแท่งเทียน BTC/USDT จริง

รัน: uv run python notebooks/00_pandas_basics.py

ทำทีละข้อ แก้ฟังก์ชัน ex1 → ex7 ให้ครบ แล้วรันใหม่ดูผล
ข้อที่ยังไม่ทำจะขึ้น "ยังไม่ทำ" ข้อที่ผิดจะขึ้น "ผิด" พร้อมเหตุผล

ไฟล์นี้เป็นสนามซ้อม ไม่ใช่โค้ดหลัก — ใช้ ccxt ตรง ๆ ได้ (ฉาก 1 ค่อยเขียน fetcher.py จริง)
"""

import sys

import ccxt
import pandas as pd

COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def load_raw() -> list[list]:
    """ให้มาแล้ว: ดึงแท่ง 1h ล่าสุด 200 แท่ง เป็น list ของ list แบบที่ ccxt ส่งมา"""
    return ccxt.binance().fetch_ohlcv("BTC/USDT", "1h", limit=200)


# ── ข้อ 1: list → DataFrame ────────────────────────────────────────────────
def ex1(raw: list[list]) -> pd.DataFrame:
    """แปลง raw เป็น DataFrame ที่:
    - มีคอลัมน์ตาม COLUMNS
    - timestamp เป็น datetime แบบ UTC (ตอนนี้เป็นมิลลิวินาที)
    - ใช้ timestamp เป็น index
    - ตัดแท่งสุดท้ายทิ้ง (ยังไม่ปิด — จำได้ไหม?)

    คำใบ้: pd.DataFrame(..., columns=...), pd.to_datetime(..., unit=..., utc=...),
           .set_index(...), .iloc[...]
    """
    df = pd.DataFrame(raw, columns=COLUMNS)
    converted_timestamp = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["timestamp"] = converted_timestamp
    df_indexed = df.set_index("timestamp")
    df_sliced = df_indexed.iloc[:-1]

    return df_sliced



# ── ข้อ 2: เลือกคอลัมน์และแถว ─────────────────────────────────────────────
def ex2(df: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """คืน (คอลัมน์ close ทั้งหมด, 5 แถวสุดท้ายเฉพาะคอลัมน์ open กับ close)

    คำใบ้: df["..."], df[[..., ...]], .tail(...)
    """
    close_series = df["close"]
    last_5_rows = df[["open", "close"]].tail(5)

    return close_series, last_5_rows


# ── ข้อ 3: สร้างคอลัมน์ใหม่ ────────────────────────────────────────────────
def ex3(df: pd.DataFrame) -> pd.DataFrame:
    """คืน df ที่เพิ่ม 3 คอลัมน์:
    - range  = high − low        (กรอบแกว่งของแท่ง — เรื่อง stop ที่คุยกัน)
    - change = close − open      (บวก = แท่งเขียว)
    - ret    = % เปลี่ยนของ close เทียบแท่งก่อนหน้า (0.01 = 1%)

    คำใบ้: คำนวณทั้งคอลัมน์ได้เลยไม่ต้อง loop; .pct_change()
    คิดดู: ทำไม ret แถวแรกเป็น NaN
    """
    columns_to_add = df
    columns_to_add["range"] = columns_to_add["high"] - columns_to_add["low"]
    columns_to_add["change"] = columns_to_add["close"] - columns_to_add["open"]
    columns_to_add["ret"] = columns_to_add["close"].pct_change()

    return columns_to_add


# ── ข้อ 4: กรองแถว ─────────────────────────────────────────────────────────
def ex4(df: pd.DataFrame) -> tuple[int, float]:
    """ใช้ df จากข้อ 3 คืน (จำนวนแท่งเขียว, range เฉลี่ยของทุกแท่ง)

    คำใบ้: df[เงื่อนไข], len(...), .mean()
    เอา range เฉลี่ยไปเทียบกับระยะ stop 300 ที่คิดกันเมื่อกี้ — แคบหรือกว้าง?
    """
    condition = df["change"] > 0
    green_count = len(df[condition])
    average_range = df["range"].mean()

    return green_count, average_range


# ── ข้อ 5: rolling — SMA ตัวแรก ───────────────────────────────────────────
def ex5(df: pd.DataFrame) -> pd.Series:
    """คืน SMA 20 ของ close

    คำใบ้: .rolling(...).mean()
    คิดดู: ค่า NaN ช่วงแรกมีกี่แถว เกี่ยวกับ warm-up ยังไง
    """
    sma_20 = df["close"].rolling(window=20).mean()
    return sma_20   


# ── ข้อ 6: shift — มองย้อนหลัง vs แอบดูอนาคต ─────────────────────────────
def ex6(df: pd.DataFrame) -> pd.Series:
    """คืนผลต่าง open ของแต่ละแท่ง − close ของแท่งก่อนหน้า (gap ระหว่างแท่ง)

    คำใบ้: .shift(1) = ค่าของแถวก่อนหน้า
    คิดดู: .shift(-1) ให้ค่าอะไร ทำไมห้ามใช้ในกลยุทธ์
    """
    close_shifted = df["close"].shift(1)
    gap = df["open"] - close_shifted
    return gap  


# ── ข้อ 7: resample — แท่ง 1h → 4h ────────────────────────────────────────
def ex7(df: pd.DataFrame) -> pd.DataFrame:
    """รวมแท่ง 1h เป็น 4h ด้วยกฎ O/H/L/C/V ที่คุณตอบไว้

    คำใบ้: .resample("4h").agg({...: "first" / "max" / "min" / "last" / "sum"})
    """
    return df.resample("4h").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"})   


# ── ตัวตรวจ (ไม่ต้องแก้) ───────────────────────────────────────────────────
def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # console Windows ค่าเริ่มต้นพิมพ์ภาษาไทยไม่ได้
    raw = load_raw()
    print(f"ดึงมา {len(raw)} แท่ง\n")

    def run(name, fn, *args):
        try:
            out = fn(*args)
        except NotImplementedError:
            print(f"{name}: ยังไม่ทำ")
            return None
        return out

    df = run("ข้อ 1", ex1, raw)
    if df is None:
        return
    ok = (
        list(df.columns) == COLUMNS[1:]
        and isinstance(df.index, pd.DatetimeIndex)
        and str(df.index.tz) == "UTC"
        and len(df) == len(raw) - 1
    )
    print("ข้อ 1:", "ผ่าน" if ok else "ผิด — เช็คคอลัมน์ / index เป็นเวลา UTC / ตัดแท่งสุดท้ายหรือยัง")
    print(df.tail(3), "\n")

    out = run("ข้อ 2", ex2, df)
    if out is not None:
        close, last5 = out
        ok = close.name == "close" and list(last5.columns) == ["open", "close"] and len(last5) == 5
        print("ข้อ 2:", "ผ่าน" if ok else "ผิด")

    df3 = run("ข้อ 3", ex3, df.copy())
    if df3 is not None:
        ok = {"range", "change", "ret"} <= set(df3.columns) and pd.isna(df3["ret"].iloc[0])
        print("ข้อ 3:", "ผ่าน" if ok else "ผิด — มีครบ 3 คอลัมน์ไหม และ ret แถวแรกควรเป็น NaN")

        out = run("ข้อ 4", ex4, df3)
        if out is not None:
            green, avg_range = out
            ok = green == int((df3["close"] > df3["open"]).sum())
            print("ข้อ 4:", "ผ่าน" if ok else "ผิด", f"— แท่งเขียว {green}, range เฉลี่ย {avg_range:.2f}")

    sma = run("ข้อ 5", ex5, df)
    if sma is not None:
        n_nan = int(sma.isna().sum())
        print("ข้อ 5:", "ผ่าน" if n_nan == 19 else "ผิด", f"— NaN {n_nan} แถว")

    gap = run("ข้อ 6", ex6, df)
    if gap is not None:
        ok = pd.isna(gap.iloc[0]) and abs(gap.iloc[1] - (df["open"].iloc[1] - df["close"].iloc[0])) < 1e-9
        print("ข้อ 6:", "ผ่าน" if ok else "ผิด", f"— gap ใหญ่สุด {gap.abs().max():.2f} USDT")

    df7 = run("ข้อ 7", ex7, df)
    if df7 is not None:
        first = df7.index[1]  # แท่งเต็มแท่งแรก (แท่งแรกอาจไม่ครบ 4 ชม.)
        chunk = df.loc[first : first + pd.Timedelta(hours=3)]
        ok = (
            len(chunk) == 4
            and df7.loc[first, "high"] == chunk["high"].max()
            and df7.loc[first, "close"] == chunk["close"].iloc[-1]
        )
        print("ข้อ 7:", "ผ่าน" if ok else "ผิด", f"— ได้ {len(df7)} แท่ง 4h")


if __name__ == "__main__":
    main()
