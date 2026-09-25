"""อ่าน/เขียนข้อมูลราคาเป็น CSV ใน data/raw/

ตั้งชื่อไฟล์ให้บอกได้ว่าเป็นข้อมูลอะไร เช่น binance_BTC-USDT_1h.csv
"""

from pathlib import Path

import pandas as pd


def save_csv(df: pd.DataFrame, path: Path) -> None:
    """TODO(ฉาก 1)"""
    raise NotImplementedError


def load_csv(path: Path) -> pd.DataFrame:
    """TODO(ฉาก 1): อย่าลืม parse คอลัมน์ timestamp กลับเป็น datetime UTC"""
    raise NotImplementedError
