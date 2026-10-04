"""เกณฑ์เทียบ: buy & hold ช่วงเดียวกัน — กลยุทธ์ต้องชนะ "ซื้อแล้วถือเฉย ๆ" ถึงจะมีความหมาย

ซื้อด้วยเงินทั้งพอร์ตที่ open แท่งแรกของช่วง ขายที่ close แท่งสุดท้าย
หัก slippage + fee ทั้งสองขาแบบเดียวกับ engine (costs.py) — กฎอยู่ที่ docs/backtesting.md หัวข้อ 4
"""

import pandas as pd

from tradebot.backtest.costs import apply_slippage, fee
from tradebot.backtest.metrics import max_drawdown


def buy_and_hold(df: pd.DataFrame, capital: float, slippage_pct: float, fee_pct: float) -> dict:
    """คืน {"net_profit", "return_pct", "max_drawdown"} ของการซื้อตอนต้นช่วงแล้วถือจนจบ

    ขนาดซื้อใช้เพดานเงินสูตรเดียวกับ sizing: เงินทั้งหมด ÷ (ราคาที่ได้จริง × (1 + fee))
    drawdown วัดจาก equity ณ close ทุกแท่ง (ถือตลอด ไม่มี stop)
    """
    buy_price = apply_slippage(float(df["open"].iloc[0]), "buy", slippage_pct)
    size = capital / (buy_price * (1 + fee_pct))

    sell_price = apply_slippage(float(df["close"].iloc[-1]), "sell", slippage_pct)
    proceeds = size * sell_price - fee(size * sell_price, fee_pct)
    net_profit = proceeds - capital

    # จุดเริ่ม = ทุนก่อนซื้อ แล้วตามด้วยมูลค่า ณ close ทุกแท่ง — แท่งสุดท้ายใช้เงินที่ขายได้จริง
    held = (size * df["close"]).to_numpy(copy=True)  # pandas 3 คืน array แบบแก้ไม่ได้ ต้อง copy
    held[-1] = proceeds
    equity = pd.Series([capital, *held])

    return {
        "net_profit": float(net_profit),
        "return_pct": float(net_profit / capital),
        "max_drawdown": max_drawdown(equity),
    }
