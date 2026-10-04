"""รัน backtest ตาม config แล้วพิมพ์ metrics + บันทึกลง docs/journal.jsonl อัตโนมัติ

รัน:
  uv run python scripts/run_backtest.py --split tune
  uv run python scripts/run_backtest.py --split test
  (holdout ยังปิดอยู่ — ต้องมี journal.count_runs ก่อน ฉาก 3)

ลำดับ (กฎอยู่ที่ docs/backtesting.md):
  config → CSV → สัญญาณจากข้อมูลเต็ม (หัวข้อ 3) → ตัดราคาและสัญญาณตามช่วง
  → engine (เริ่มพอร์ตว่างทุกช่วง) → metrics → พิมพ์ → journal ทุกครั้ง ไม่มีข้อยกเว้น (หัวข้อ 4)

ก่อนรัน: commit โค้ดให้หมด ไม่อย่างนั้นบรรทัดใน journal จะเป็น git_dirty = true (ย้อนทำซ้ำไม่ได้)
ดึงข้อมูลใหม่ / เปลี่ยนคู่เทรด → รัน notebooks/01_data_check.py ก่อน (หัวข้อ 7)
"""

import argparse
import sys

from tradebot.backtest import metrics
from tradebot.backtest.engine import run_backtest
from tradebot.backtest.journal import append_entry
from tradebot.backtest.splits import SPLIT_ORDER, split_slices
from tradebot.config import load_config
from tradebot.data.storage import load_csv, raw_csv_path
from tradebot.strategies.sma_cross import SmaCross

STRATEGIES = {"sma_cross": SmaCross}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="รัน backtest หนึ่งช่วงข้อมูล แล้วบันทึกลง journal")
    parser.add_argument("--split", required=True, choices=SPLIT_ORDER)
    return parser.parse_args()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    if args.split == "holdout":
        # holdout แตะได้ครั้งเดียว — ต้องมี journal.count_runs กันการรันซ้ำก่อน (ฉาก 3)
        sys.exit("holdout ยังปิดอยู่ — ต้องทำ journal.count_runs ก่อน (ฉาก 3)")

    config = load_config()
    market, costs, risk = config["market"], config["costs"], config["risk"]
    strategy_cfg = config["strategy"]
    strategy = STRATEGIES[strategy_cfg["name"]](**strategy_cfg["params"])

    df = load_csv(raw_csv_path(market))
    signals = strategy.generate_signals(df)  # ข้อมูลเต็มก่อนตัด (หัวข้อ 3)

    part = split_slices(len(df), config["splits"])[args.split]
    df_split, signals_split = df.iloc[part], signals.iloc[part]

    result = run_backtest(df_split, signals_split, config)
    trades, equity = result.trades, result.equity_curve

    results = {
        "net_profit": metrics.net_profit(trades),
        "expectancy": metrics.expectancy(trades),
        "profit_factor": metrics.profit_factor(trades),
        "max_drawdown": metrics.max_drawdown(equity),
        "win_rate": metrics.win_rate(trades),
        "n_trades": len(trades),
        "n_capped": result.n_capped,
        "max_losing_streak": metrics.max_losing_streak(trades),
        "worst_day_pct": metrics.worst_day_pct(equity),
    }

    entry = {
        "strategy": strategy.name,
        "params": strategy_cfg["params"],
        "data": {
            "symbol": market["symbol"],
            "timeframe": market["timeframe"],
            "start": df_split.index[0].isoformat(),
            "end": df_split.index[-1].isoformat(),
        },
        "split": args.split,
        "costs": {"fee_pct": costs["fee_pct"], "slippage_pct": costs["slippage_pct"]},
        "risk": {
            "risk_per_trade_pct": risk["risk_per_trade_pct"],
            "stop_method": risk["stop_method"],
            "stop_pct": risk["stop_pct"],
        },
        "results": results,
    }
    append_entry(entry)  # ทุกครั้ง รวมรอบที่ผลไม่สวย

    print(
        f"{strategy.name} {strategy_cfg['params']} | {args.split}: {entry['data']['start']} → "
        f"{entry['data']['end']} ({len(df_split)} แท่ง)"
    )
    print(
        f"  net profit      {results['net_profit']:>12,.2f} USDT "
        f"({results['net_profit'] / risk['initial_capital']:+.2%})"
    )
    print(f"  expectancy      {results['expectancy']:>12,.2f} USDT/ไม้")
    print(f"  profit factor   {results['profit_factor']:>12.3f}")
    print(f"  max drawdown    {results['max_drawdown']:>12.2%}")
    print(f"  win rate        {results['win_rate']:>12.2%}")
    print(f"  ไม้ / ถูกตัดขนาด {results['n_trades']:>8} / {results['n_capped']}")
    print(f"  แพ้ติดกันมากสุด  {results['max_losing_streak']:>8} ไม้")
    print(f"  วันแย่สุด        {results['worst_day_pct']:>12.2%}")
    print("บันทึกลง docs/journal.jsonl แล้ว")


if __name__ == "__main__":
    main()
