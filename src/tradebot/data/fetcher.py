"""ดึงข้อมูลแท่งเทียน (OHLCV) จาก exchange ผ่าน ccxt

ผลลัพธ์: DataFrame คอลัมน์ timestamp (UTC), open, high, low, close, volume
เรียงจากเก่าไปใหม่ ไม่มีแถวซ้ำ
"""

import ccxt
import pandas as pd

COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def fetch_ohlcv(exchange: str, symbol: str, timeframe: str, days: int) -> pd.DataFrame:
    """ดึงข้อมูลย้อนหลัง `days` วัน"""
    ex = getattr(ccxt, exchange)()
    day_ms = 24 * 60 * 60 * 1000
    now = ex.milliseconds()
    bar_ms = ex.parse_timeframe(timeframe) * 1000
    since = now - days * day_ms
    rows = []

    while since < now:
        page = ex.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if not page:
            break
        rows.extend(page)
        since = page[-1][0] + bar_ms

    df = pd.DataFrame(rows, columns=COLUMNS)
    df = df.drop_duplicates(subset="timestamp")
    df = df[df["timestamp"] + bar_ms <= now]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)

    return df.set_index("timestamp").sort_index()
