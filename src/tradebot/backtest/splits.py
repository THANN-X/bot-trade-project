"""แบ่งข้อมูลเป็นช่วง จูน / ทดสอบ / holdout ตามเวลา — กฎอยู่ที่ docs/backtesting.md หัวข้อ 3

แบ่งตามจำนวนแถว เรียงเก่า → ใหม่ ช่วงต่อกันพอดี ไม่ซ้อน ไม่ตกหล่น
"""

SPLIT_ORDER = ("tune", "test", "holdout")


def split_slices(n_rows: int, splits: dict) -> dict[str, slice]:
    """คืน slice ของแต่ละช่วง เช่น 100 แถว 0.6/0.2/0.2 → tune 0:60, test 60:80, holdout 80:100

    splits — config["splits"] สัดส่วนรวมกันต้องได้ 1.0 ไม่อย่างนั้น raise ValueError
    ช่วงสุดท้ายจบที่ n_rows เสมอ เศษจากการปัดจึงไม่ทำให้แถวท้ายหาย
    """
    total = sum(splits[name] for name in SPLIT_ORDER)
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"splits ต้องรวมกันได้ 1.0 ได้ {total}")

    slices = {}
    start = 0
    cumulative = 0.0
    for name in SPLIT_ORDER:
        cumulative += splits[name]
        end = n_rows if name == SPLIT_ORDER[-1] else int(n_rows * cumulative)
        slices[name] = slice(start, end)
        start = end
    return slices
