"""ดึงข้อมูลราคาตาม config แล้วเก็บลง data/raw/

รัน: uv run python scripts/fetch_data.py

load_config → fetch_ohlcv → save_csv → plot_price
"""

from tradebot.config import PROJECT_ROOT, load_config
from tradebot.data.fetcher import fetch_ohlcv
from tradebot.data.storage import raw_csv_path, save_csv
from tradebot.viz.plot import plot_price


def main() -> None:
    config = load_config()  # โหลด config จากไฟล์ config.yaml
    market = config["market"]  # ดึงข้อมูลตลาดจาก config
    ohlcv_data = fetch_ohlcv(
        market["exchange"], market["symbol"], market["timeframe"], market["history_days"]
    )  # ดึงข้อมูล OHLCV จาก exchange ตาม config

    # path ของ CSV มาจาก storage.raw_csv_path — run_backtest.py ใช้ฟังก์ชันเดียวกันตอนอ่าน
    csv_path = raw_csv_path(market)
    # สร้าง path สำหรับเก็บไฟล์ PNG (ชื่อเดียวกับ CSV แต่อยู่ใน reports/)
    png_path = (PROJECT_ROOT / "reports" / csv_path.name).with_suffix(".png")
    # สร้างโฟลเดอร์สำหรับเก็บไฟล์ PNG หากยังไม่มี
    png_path.parent.mkdir(parents=True, exist_ok=True)

    # บันทึกข้อมูล OHLCV ลงไฟล์ CSV และสร้างกราฟราคา
    save_csv(ohlcv_data, csv_path)
    # สร้างกราฟราคาและบันทึกเป็นไฟล์ PNG
    fig = plot_price(ohlcv_data)

    # บันทึกกราฟราคาเป็นไฟล์ PNG
    fig.savefig(png_path)

    print(f"OHLCV Data: {ohlcv_data.shape[0]} rows")
    print(f"Date Range: {ohlcv_data.index[0]} to {ohlcv_data.index[-1]}")


if __name__ == "__main__":
    main()
