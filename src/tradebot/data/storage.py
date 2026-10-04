"""อ่าน/เขียนข้อมูลราคาเป็น CSV ใน data/raw/

ตั้งชื่อไฟล์ให้บอกได้ว่าเป็นข้อมูลอะไร เช่น binance_BTC-USDT_1h.csv
"""

from pathlib import Path

import pandas as pd

from tradebot.config import PROJECT_ROOT


def raw_csv_path(market: dict) -> Path:
    """path ของไฟล์ข้อมูลดิบจาก config["market"] เช่น data/raw/binance_BTC-USDT_1h.csv

    "/" ใน symbol เปลี่ยนเป็น "-" ไม่อย่างนั้นจะกลายเป็นโฟลเดอร์ย่อย
    fetch_data.py เขียนไฟล์นี้ run_backtest.py อ่านไฟล์นี้ — ใช้ฟังก์ชันเดียวกัน ชื่อจึงตรงกันเสมอ
    """
    symbol_for_file = market["symbol"].replace("/", "-")
    name = f"{market['exchange']}_{symbol_for_file}_{market['timeframe']}.csv"
    return PROJECT_ROOT / "data" / "raw" / name


def save_csv(df: pd.DataFrame, path: Path) -> None:
    "เขียน DataFrame เป็น CSV สร้างโฟลเดอร์ให้ถ้ายังไม่มี"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=True)


def load_csv(path: Path) -> pd.DataFrame:
    "อ่าน CSV กลับมาโดยใช้ timestamp (UTC) เป็น index"
    df = pd.read_csv(path, index_col="timestamp", parse_dates=True)
    return df
