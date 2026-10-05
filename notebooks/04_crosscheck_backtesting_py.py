"""ฉาก 3 — ตรวจ engine ของเราเทียบ backtesting.py (ปิดค่าใช้จ่าย)

รัน: uv run python notebooks/04_crosscheck_backtesting_py.py

จุดประสงค์: ยืนยันว่า engine ไม่มีบั๊ก ก่อนเชื่อผลใน journal — ไม่ใช่ทดลองกลยุทธ์
จึงใช้ config เดิมทุกอย่าง แค่ตั้ง fee / slippage = 0 และไม่เขียน journal

ความต่างของกติกาที่ต้องปรับให้ตรงกันก่อนเทียบ:
  1. backtesting.py ไม่เรียก next() ที่แท่งแรก → เติมแท่งหลอกไว้หน้าข้อมูล 1 แท่ง
  2. backtesting.py ปิดไม้ค้างที่ open แท่งสุดท้าย แต่ของเราปิดที่ close (หัวข้อ 3)
     → เติมแท่งหลอกท้ายข้อมูล 1 แท่ง ให้ open = close สุดท้ายของเรา
  3. backtesting.py ซื้อได้ทีละ 1 หน่วยเต็ม → หารราคาด้วย 1e8 (1 หน่วย = 1 satoshi)
     ขนาดไม้ปัดลงเป็น satoshi เต็ม → ต่างจากของเราไม่เกิน 1 satoshi ต่อไม้
  4. ของเราคิดขนาดไม้และ stop จากราคาเข้าจริง (open แท่งถัดไป) → ฝั่ง backtesting.py
     ต้องหยิบ open แท่งถัดไปจากข้อมูลเต็มมาคิด (ทำได้เพราะเป็นตัวตรวจ ไม่ใช่กลยุทธ์)
"""

import copy
import math
import sys
import warnings

import pandas as pd
from backtesting import Backtest
from backtesting import Strategy as BtStrategy

from tradebot.backtest.engine import run_backtest
from tradebot.backtest.splits import split_slices
from tradebot.config import load_config
from tradebot.data.storage import load_csv, raw_csv_path
from tradebot.risk.sizing import position_size
from tradebot.risk.stops import stop_price
from tradebot.strategies.base import Signal
from tradebot.strategies.sma_cross import SmaCross

SCALE = 1e-8  # 1 หน่วยใน backtesting.py = 1 satoshi


def to_backtesting_frame(df: pd.DataFrame) -> pd.DataFrame:
    """แปลงเป็นรูปแบบของ backtesting.py + เติมแท่งหลอกหน้า/ท้าย (ข้อ 1, 2) + scale ราคา (ข้อ 3)"""
    one_hour = df.index[1] - df.index[0]
    first, last_close = df.iloc[0], df["close"].iloc[-1]
    head = pd.DataFrame([[first["open"]] * 4], index=[df.index[0] - one_hour])
    tail = pd.DataFrame([[last_close] * 4], index=[df.index[-1] + one_hour])
    body = pd.DataFrame(df[["open", "high", "low", "close"]].to_numpy(), index=df.index)
    out = pd.concat([head, body, tail])
    out.columns = ["Open", "High", "Low", "Close"]
    out = out * SCALE
    out["Volume"] = 1.0
    out.index = out.index.tz_localize(None)
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    warnings.filterwarnings("ignore")

    config = copy.deepcopy(load_config())
    config["costs"]["fee_pct"] = 0.0
    config["costs"]["slippage_pct"] = 0.0
    risk = config["risk"]

    df_full = load_csv(raw_csv_path(config["market"]))
    signals_full = SmaCross(**config["strategy"]["params"]).generate_signals(df_full)
    part = split_slices(len(df_full), config["splits"])["tune"]
    df, signals = df_full.iloc[part], signals_full.iloc[part]

    # ── engine ของเรา ──
    ours = run_backtest(df, signals, config)

    # ── backtesting.py ──
    opens = df["open"].to_numpy()
    sig = signals.to_numpy()

    class Replay(BtStrategy):
        def init(self):
            pass

        def next(self):
            i = len(self.data) - 2  # ลำดับแท่งในข้อมูลของเรา (หักแท่งหลอกหน้า)
            if i >= len(sig) - 1:  # แท่งสุดท้ายของเรา: ไม่ใช้สัญญาณ (หัวข้อ 3)
                return
            if sig[i] == Signal.SELL and self.position:
                self.position.close()
            elif sig[i] == Signal.BUY and not self.position:
                fill = float(opens[i + 1])  # ราคาเข้าจริง (ข้อ 4)
                stop = stop_price(fill, risk)
                units, _ = position_size(self.equity, risk["risk_per_trade_pct"], fill, stop)
                self.buy(size=math.floor(units / SCALE), sl=stop * SCALE)

    bt = Backtest(
        to_backtesting_frame(df),
        Replay,
        cash=risk["initial_capital"],
        commission=0,
        finalize_trades=True,
    )
    stats = bt.run()
    theirs = stats._trades

    # ── เทียบ ──
    print(f"ช่วงจูน {df.index[0]} → {df.index[-1]} ({len(df)} แท่ง) ปิดค่าใช้จ่าย\n")
    print(f"{'':24}{'ของเรา':>14}{'backtesting.py':>16}")
    print(f"{'จำนวนไม้':<24}{len(ours.trades):>14}{len(theirs):>16}")
    our_final = ours.equity_curve.iloc[-1]
    their_final = stats["Equity Final [$]"]
    print(f"{'equity สุดท้าย':<24}{our_final:>14,.2f}{their_final:>16,.2f}")
    print(f"{'ต่างกัน':<24}{our_final - their_final:>14,.4f}")

    n = min(len(ours.trades), len(theirs))
    mismatches = []
    for k in range(n):
        o, t = ours.trades[k], theirs.iloc[k]
        entry_ok = math.isclose(o.entry_price, t["EntryPrice"] / SCALE, rel_tol=1e-9)
        exit_ok = math.isclose(o.exit_price, t["ExitPrice"] / SCALE, rel_tol=1e-9)
        time_ok = o.entry_time.tz_localize(None) == t["EntryTime"]
        if not (entry_ok and exit_ok and time_ok):
            mismatches.append((k, o, t))
    print(f"\nไม้ที่ราคาเข้า/ออกหรือเวลาเข้าไม่ตรงกัน: {len(mismatches)} จาก {n}")
    for k, o, t in mismatches[:5]:
        print(
            f"  ไม้ {k}: ของเรา {o.entry_time} {o.entry_price:.2f}→{o.exit_price:.2f} ({o.exit_reason})"
            f" | bt {t['EntryTime']} {t['EntryPrice'] / SCALE:.2f}→{t['ExitPrice'] / SCALE:.2f}"
        )

    pnl_diff = max(abs(o.pnl - theirs.iloc[k]["PnL"]) for k, o in enumerate(ours.trades[:n]))
    print(f"pnl ต่อไม้ต่างกันมากสุด: {pnl_diff:.6f} USDT (ขนาดปัดเป็น satoshi)")


if __name__ == "__main__":
    main()
