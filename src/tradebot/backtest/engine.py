"""Backtest engine — เดินทีละแท่ง จำลองการเข้า/ออกออเดอร์ (long อย่างเดียว ถือทีละไม้)

กฎทั้งหมดอยู่ใน docs/backtesting.md ที่เดียว — ที่นี่เป็นแค่สรุปพร้อมเลขหัวข้อ
ถ้ากฎเปลี่ยน แก้ที่ backtesting.md ก่อน แล้วค่อยแก้โค้ดให้ตรง

รับสัญญาณที่คำนวณจากข้อมูลเต็มมาแล้ว ไม่คำนวณใหม่ (หัวข้อ 3, 5)
→ จึงรับ signals เข้ามาตรง ๆ ไม่ได้รับ strategy

ลำดับในแท่ง t (tests/test_engine.py ตรวจทีละข้อ):
  1. ถือไม้อยู่ และ open ≤ stop → ปิดที่ open, exit_reason "stop"   — หัวข้อ 6 (gap)
  2. สัญญาณของแท่ง t−1:                                            — หัวข้อ 1
     SELL + ถือไม้ → ปิดที่ open, exit_reason "signal"
     BUY + ไม่ถือ → เข้าที่ open + slippage, stop จาก risk/stops.py,
                    ขนาดจาก risk/sizing.py (capped → n_capped += 1)  — หัวข้อ 2, 6
     กรณีอื่น (SELL ตอนไม่ถือ, BUY ตอนถืออยู่) → ไม่ทำอะไร
  3. ถือไม้อยู่ และ low ≤ stop → ปิดที่ราคา stop, exit_reason "stop"  — หัวข้อ 6
     (แท่งที่เพิ่งเข้า ข้อ 1 ไม่มีผลเพราะเข้าที่ open พอดี เหลือแค่ข้อนี้)
  4. บันทึก equity = เงินสด + จำนวนเหรียญ × close
แท่งสุดท้าย: ยังถือ → ปิดที่ close, exit_reason "end"; สัญญาณแท่งสุดท้ายไม่ถูกใช้   — หัวข้อ 3

ทุกการซื้อขาย: หัก slippage แล้วคิด fee จากมูลค่าหลังหัก slippage (costs.py)        — หัวข้อ 2
kill switch: ยังไม่ต่อ — ฉาก 3
"""

from dataclasses import dataclass, field

import pandas as pd

from tradebot.backtest.costs import apply_slippage, fee
from tradebot.risk.sizing import position_size
from tradebot.risk.stops import stop_price
from tradebot.strategies.base import Signal


@dataclass
class Trade:
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry_price: float  # ราคาที่ได้จริง (หลังบวก slippage)
    exit_price: float  # ราคาที่ได้จริง (หลังหัก slippage)
    size: float
    pnl: float  # เงินที่ได้ตอนออก − เงินที่จ่ายตอนเข้า (รวม fee ทั้งสองขาแล้ว)
    fees: float  # fee ขาเข้า + ขาออก
    exit_reason: str  # "signal" | "stop" | "end"


@dataclass
class BacktestResult:
    trades: list[Trade] = field(default_factory=list)
    equity_curve: pd.Series | None = None  # index เดียวกับ df, ค่า ณ close ของแต่ละแท่ง
    n_capped: int = 0  # ไม้ที่ขนาดถูกตัดด้วยเพดานเงิน (backtesting.md หัวข้อ 2)


def close_position(
    pos: dict, raw_price: float, time, reason: str, slippage_pct: float, fee_pct: float
) -> tuple[Trade, float]:
    """ปิดไม้: คืน (Trade ที่ปิดแล้ว, เงินสดที่ได้คืน)"""

    sell_price = apply_slippage(raw_price, "sell", slippage_pct)
    fee_out = fee(pos["size"] * sell_price, fee_pct)
    proceeds = pos["size"] * sell_price - fee_out
    trade = Trade(
        entry_time=pos["entry_time"],
        exit_time=time,
        entry_price=pos["entry_price"],
        exit_price=sell_price,
        size=pos["size"],
        pnl=proceeds - (pos["size"] * pos["entry_price"] + pos["fee"]),
        fees=pos["fee"] + fee_out,
        exit_reason=reason,
    )
    return trade, proceeds


def run_backtest(df: pd.DataFrame, signals: pd.Series, config: dict) -> BacktestResult:
    """จำลองการเทรดบน df (ช่วงเดียว เริ่มพอร์ตว่าง) ด้วยสัญญาณที่คำนวณไว้แล้ว
    df      — OHLCV ช่วงที่ต้องการ (index เวลา UTC)
    signals — Series ของ Signal index เดียวกับ df
    config  — ใช้ config["costs"] และ config["risk"]
    """
    cash = config["risk"]["initial_capital"]  # เงินสดเริ่มต้น
    pos: dict | None = (
        None  # None = ไม่ถือ, dict = ถืออยู่ {"entry_time", "entry_price", "size", "stop"}
    )
    trades = []  # list[Trade]
    equity = []  # list[float] เงินสด + จำนวนเหรียญ × close ของแต่ละแท่ง
    n_capped = 0

    slippage = config["costs"]["slippage_pct"]
    fee_pct = config["costs"]["fee_pct"]

    for i, (time, bar) in enumerate(df.iterrows()):
        # ขั้น 1: open กระโดดข้าม stop → ปิดที่ open
        if pos is not None and bar["open"] <= pos["stop"]:
            trade, proceeds = close_position(pos, bar["open"], time, "stop", slippage, fee_pct)
            trades.append(trade)
            cash += proceeds
            pos = None

        # ขั้น 2: สัญญาณของแท่งก่อนหน้า
        if i > 0:
            prev_signal = signals.iloc[i - 1]
            if prev_signal == Signal.SELL and pos is not None:
                trade, proceeds = close_position(
                    pos, bar["open"], time, "signal", slippage, fee_pct
                )
                trades.append(trade)
                cash += proceeds
                pos = None

            elif prev_signal == Signal.BUY and pos is None:
                buy_price = apply_slippage(bar["open"], "buy", slippage)
                stop = stop_price(buy_price, config["risk"])
                # buy_price บวก slippage แล้ว → sizing รับแค่ fee (ไม่นับ slippage ซ้ำ)
                size, capped = position_size(
                    cash, config["risk"]["risk_per_trade_pct"], buy_price, stop, fee_pct=fee_pct
                )
                fee_in = fee(size * buy_price, fee_pct)
                cash -= size * buy_price + fee_in
                pos = {
                    "entry_time": time,
                    "entry_price": buy_price,
                    "size": size,
                    "stop": stop,
                    "fee": fee_in,
                }
                n_capped += capped

        # ขั้น 3: low แตะ stop → ปิดที่ราคา stop
        if pos is not None and bar["low"] <= pos["stop"]:
            trade, proceeds = close_position(pos, pos["stop"], time, "stop", slippage, fee_pct)
            trades.append(trade)
            cash += proceeds
            pos = None

        # แท่งสุดท้ายของช่วง: ยังถือ → ปิดที่ close (หัวข้อ 3)
        if pos is not None and i == len(df) - 1:
            trade, proceeds = close_position(pos, bar["close"], time, "end", slippage, fee_pct)
            trades.append(trade)
            cash += proceeds
            pos = None

        # ขั้น 4: จดมูลค่าพอร์ต ณ close ของแท่งนี้
        if pos is None:
            equity.append(cash)
        else:
            equity.append(cash + pos["size"] * bar["close"])

    return BacktestResult(trades, pd.Series(equity, index=df.index), n_capped)
