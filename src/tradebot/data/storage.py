"""อ่าน/เขียนข้อมูลราคาเป็น CSV ใน data/raw/

ตั้งชื่อไฟล์ให้บอกได้ว่าเป็นข้อมูลอะไร เช่น binance_BTC-USDT_1h.csv
"""

from pathlib import Path

import pandas as pd


def save_csv(df: pd.DataFrame, path: Path) -> None:
    "เขียน DataFrame เป็น CSV สร้างโฟลเดอร์ให้ถ้ายังไม่มี"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=True)


def load_csv(path: Path) -> pd.DataFrame:
    "อ่าน CSV กลับมาโดยใช้ timestamp (UTC) เป็น index"
    df = pd.read_csv(path, index_col="timestamp", parse_dates=True)
    return df
