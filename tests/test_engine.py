"""Backtest engine — กฎ 8 ข้อ ทำให้เขียวทีละเลข (กฎอยู่ใน docs/backtesting.md)

ข้อมูลเล็กที่คิดเลขมือได้: ราคาแถว 100, พอร์ต 10,000, เสี่ยง 1%, stop 2%
→ เข้าที่ 100: stop 98, ระยะ 2, ยอมเสีย 100 → ขนาด 50 เหรียญ (มูลค่า 5,000 ไม่ชนเพดาน)
test ส่วนใหญ่ปิดค่าใช้จ่ายไว้ (0) เพื่อดูตรรกะล้วน ๆ — test 1b เปิดค่าใช้จ่ายจริง

รัน: uv run pytest tests/test_engine.py -v
"""

import pandas as pd
import pytest

from tradebot.backtest.engine import run_backtest
from tradebot.strategies.base import Signal

CAPITAL = 10_000
SIGNAL_CODES = {"B": Signal.BUY, "S": Signal.SELL, ".": Signal.HOLD}


def bars(*ohlc: tuple[float, float, float, float]) -> pd.DataFrame:
    """แท่งเทียน 1h เรียงจาก (open, high, low, close)"""
    idx = pd.date_range("2024-01-01", periods=len(ohlc), freq="1h", tz="UTC")
    return pd.DataFrame(ohlc, index=idx, columns=["open", "high", "low", "close"]).assign(
        volume=1.0
    )


def sigs(df: pd.DataFrame, codes: str) -> pd.Series:
    """สัญญาณจากตัวอักษร: B = BUY, S = SELL, . = HOLD — หนึ่งตัวต่อแท่ง"""
    assert len(codes) == len(df)
    return pd.Series([SIGNAL_CODES[c] for c in codes], index=df.index)


def config(slippage: float = 0.0, fee: float = 0.0, stop_pct: float = 0.02) -> dict:
    return {
        "costs": {"fee_pct": fee, "slippage_pct": slippage},
        "risk": {
            "risk_per_trade_pct": 0.01,
            "initial_capital": CAPITAL,
            "stop_method": "pct",
            "stop_pct": stop_pct,
        },
    }


# ── 1. BUY แท่ง i → เข้าที่ open แท่ง i+1 (หัวข้อ 1) ─────────────────────────
def test_1_buy_enters_at_next_open():
    df = bars(
        (99.0, 100.0, 98.5, 99.5),  # 0: BUY
        (100.0, 101.0, 99.0, 100.5),  # 1: เข้าที่ open 100
        (100.5, 101.0, 100.0, 101.0),  # 2: แท่งสุดท้าย
    )
    result = run_backtest(df, sigs(df, "B.."), config())

    trade = result.trades[0]
    assert trade.entry_time == df.index[1]
    assert trade.entry_price == pytest.approx(100.0)
    assert trade.size == pytest.approx(50.0)


def test_1b_costs_on_entry_and_exit():
    """เปิดค่าใช้จ่ายจริง: เข้า 100 × 1.0005 = 100.05, stop 2% จากราคาที่ได้จริง (หัวข้อ 2, 6)
    ออกตอนจบที่ close 101 × 0.9995 = 100.9495, fee 0.1% ของมูลค่าแต่ละขา
    """
    df = bars(
        (99.0, 100.0, 98.5, 99.5),
        (100.0, 101.0, 99.0, 100.5),
        (100.5, 101.5, 100.0, 101.0),
    )
    result = run_backtest(df, sigs(df, "B.."), config(slippage=0.0005, fee=0.001))
    trade = result.trades[0]

    entry, exit_ = 100.05, 100.9495
    size = 100 / (entry * 0.02)  # ยอมเสีย 100 ÷ ระยะ stop (100.05 × 2%)
    fee_in, fee_out = size * entry * 0.001, size * exit_ * 0.001

    assert trade.entry_price == pytest.approx(entry)
    assert trade.exit_price == pytest.approx(exit_)
    assert trade.size == pytest.approx(size)
    assert trade.fees == pytest.approx(fee_in + fee_out)
    assert trade.pnl == pytest.approx((size * exit_ - fee_out) - (size * entry + fee_in))


# ── 2. SELL → ออกที่ open แท่งถัดไป (หัวข้อ 2) ──────────────────────────────
def test_2_sell_exits_at_next_open():
    df = bars(
        (99.0, 100.0, 98.5, 99.5),  # 0: BUY
        (100.0, 102.0, 99.5, 101.0),  # 1: เข้า 100
        (101.0, 103.0, 100.5, 102.0),  # 2: SELL
        (102.5, 103.0, 101.0, 102.0),  # 3: ออกที่ open 102.5
        (102.0, 102.5, 101.5, 102.0),  # 4
    )
    result = run_backtest(df, sigs(df, "B.S.."), config())

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_time == df.index[3]
    assert trade.exit_price == pytest.approx(102.5)
    assert trade.exit_reason == "signal"
    assert trade.pnl == pytest.approx(50 * 2.5)


# ── 3. low แตะ stop → ปิดที่ราคา stop (หัวข้อ 6 ข้อ 2) ───────────────────────
def test_3_low_touches_stop_exits_at_stop():
    df = bars(
        (99.0, 100.0, 98.5, 99.5),  # 0: BUY
        (100.0, 101.0, 99.0, 100.5),  # 1: เข้า 100, stop 98
        (99.5, 100.0, 97.5, 99.0),  # 2: low 97.5 ≤ 98 → ออกที่ 98
        (99.0, 99.5, 98.5, 99.0),  # 3
    )
    result = run_backtest(df, sigs(df, "B..."), config())

    trade = result.trades[0]
    assert trade.exit_time == df.index[2]
    assert trade.exit_price == pytest.approx(98.0)
    assert trade.exit_reason == "stop"
    assert trade.pnl == pytest.approx(-100.0)  # เสียพอดี 1% ของพอร์ต


# ── 4. open กระโดดข้าม stop → ปิดที่ open (หัวข้อ 6 ข้อ 1) ──────────────────
def test_4_gap_below_stop_exits_at_open():
    df = bars(
        (99.0, 100.0, 98.5, 99.5),  # 0: BUY
        (100.0, 101.0, 99.0, 100.5),  # 1: เข้า 100, stop 98
        (97.0, 97.5, 96.0, 97.0),  # 2: เปิดที่ 97 ต่ำกว่า stop → ออกที่ 97 ไม่ใช่ 98
        (97.0, 97.5, 96.5, 97.0),  # 3
    )
    result = run_backtest(df, sigs(df, "B..."), config())

    trade = result.trades[0]
    assert trade.exit_time == df.index[2]
    assert trade.exit_price == pytest.approx(97.0)
    assert trade.exit_reason == "stop"
    assert trade.pnl == pytest.approx(-150.0)  # เสียเกิน 1% — gap ทำให้ stop ไม่ได้ราคา


# ── 5. แท่งที่เพิ่งเข้าไม้ → เช็ค low ภายในแท่งเดียวกัน (หัวข้อ 6) ──────────
def test_5_stop_can_hit_on_entry_bar():
    df = bars(
        (99.0, 100.0, 98.5, 99.5),  # 0: BUY
        (100.0, 100.5, 97.0, 99.0),  # 1: เข้า 100 แล้ว low 97 แตะ stop 98 ในแท่งเดียวกัน
        (99.0, 99.5, 98.5, 99.0),  # 2
    )
    result = run_backtest(df, sigs(df, "B.."), config())

    trade = result.trades[0]
    assert trade.entry_time == trade.exit_time == df.index[1]
    assert trade.exit_price == pytest.approx(98.0)
    assert trade.exit_reason == "stop"


# ── 6. แท่งสุดท้าย: ปิดไม้ค้างที่ close, ไม่ใช้สัญญาณแท่งสุดท้าย (หัวข้อ 3) ─
def test_6_open_position_closed_at_last_close():
    df = bars(
        (99.0, 100.0, 98.5, 99.5),  # 0: BUY
        (100.0, 101.0, 99.0, 100.5),  # 1: เข้า 100
        (101.0, 103.5, 100.5, 103.0),  # 2: แท่งสุดท้าย → ปิดที่ close 103
    )
    result = run_backtest(df, sigs(df, "B.."), config())

    trade = result.trades[0]
    assert trade.exit_time == df.index[2]
    assert trade.exit_price == pytest.approx(103.0)
    assert trade.exit_reason == "end"


def test_6b_signal_on_last_bar_is_ignored():
    """BUY ที่แท่งสุดท้ายจะเข้าที่ open แท่งถัดไป ซึ่งอยู่นอกช่วง → ไม่มีไม้"""
    df = bars(
        (99.0, 100.0, 98.5, 99.5),
        (100.0, 101.0, 99.0, 100.5),
        (100.5, 101.0, 100.0, 101.0),  # BUY ที่นี่
    )
    result = run_backtest(df, sigs(df, "..B"), config())

    assert result.trades == []
    assert (result.equity_curve == CAPITAL).all()


# ── 7. หลังโดน stop รอ BUY ใหม่, SELL ตอนไม่ถือไม่ทำอะไร (หัวข้อ 6) ────────
def test_7_after_stop_wait_for_next_buy():
    df = bars(
        (99.0, 100.0, 98.5, 99.5),  # 0: BUY
        (100.0, 100.5, 99.5, 100.0),  # 1: เข้า 100, stop 98
        (99.5, 100.0, 97.0, 98.5),  # 2: โดน stop ที่ 98
        (98.5, 99.5, 98.0, 99.0),  # 3: SELL ← ตอนนั้นไม่ถือไม้ ต้องไม่เกิดอะไร
        (99.0, 100.0, 98.5, 99.5),  # 4
        (99.5, 100.5, 99.0, 100.0),  # 5: BUY ใหม่
        (101.0, 102.0, 100.5, 101.5),  # 6: เข้า 101 (แท่งสุดท้าย → ปิดที่ close 101.5)
    )
    result = run_backtest(df, sigs(df, "B..S.B."), config())

    assert len(result.trades) == 2
    first, second = result.trades
    assert first.exit_reason == "stop"
    assert second.entry_time == df.index[6]
    assert second.entry_price == pytest.approx(101.0)

    equity_after_first = CAPITAL - 100  # เสีย 100 จากไม้แรก
    expected_size = equity_after_first * 0.01 / (101.0 * 0.02)  # ขนาดใช้ equity ปัจจุบัน
    assert second.size == pytest.approx(expected_size)


# ── 8. equity curve และ n_capped (หัวข้อ 2, 4) ───────────────────────────────
def test_8_equity_curve_marks_to_close():
    df = bars(
        (99.0, 100.0, 98.5, 99.5),  # 0: ยังไม่ถือ → 10,000
        (100.0, 101.0, 99.0, 100.5),  # 1: ถือ 50 เหรียญ → 10,000 − 5,000 + 50 × 100.5
        (100.5, 101.5, 100.0, 101.0),  # 2: ปิดที่ close 101 → 10,000 + 50
    )
    result = run_backtest(df, sigs(df, "B.."), config())

    assert result.equity_curve.index.equals(df.index)
    assert list(result.equity_curve) == pytest.approx([10_000, 10_025, 10_050])
    assert result.equity_curve.iloc[-1] == pytest.approx(
        CAPITAL + sum(t.pnl for t in result.trades)
    )


def test_8b_n_capped_counts_trimmed_trades():
    """stop 0.1% → ระยะ 0.1 → ตามความเสี่ยงอยากได้ 1,000 เหรียญ (100,000 USDT) เกินพอร์ต → ตัดเหลือ 100"""
    df = bars(
        (99.0, 100.0, 98.5, 99.5),
        (100.0, 101.0, 99.95, 100.5),  # low 99.95 ยังไม่แตะ stop 99.9
        (100.5, 101.0, 100.0, 101.0),
    )
    result = run_backtest(df, sigs(df, "B.."), config(stop_pct=0.001))

    assert result.n_capped == 1
    assert type(result.n_capped) is int  # ไม่ใช่ numpy int64 — journal เขียนได้
    assert result.trades[0].size == pytest.approx(100.0)


def test_8c_capped_buy_with_costs_spends_all_cash():
    """ชนเพดาน + เปิดค่าใช้จ่ายจริง → ค่าเหรียญ + fee ขาเข้า ต้องเท่ากับเงินทั้งพอร์ตพอดี
    จับบั๊ก "นับ slippage ซ้ำ" (engine บวก slippage แล้ว sizing บวกอีก → เหลือเงินค้าง ~5 USDT)
    """
    df = bars(
        (99.0, 100.0, 98.5, 99.5),
        (100.0, 101.0, 100.0, 100.5),  # เข้า 100.05, stop 0.1% ≈ 99.95 → low 100 ไม่แตะ
        (100.5, 101.0, 100.2, 101.0),
    )
    result = run_backtest(df, sigs(df, "B.."), config(slippage=0.0005, fee=0.001, stop_pct=0.001))
    trade = result.trades[0]

    spent = trade.size * trade.entry_price * (1 + 0.001)
    assert result.n_capped == 1
    assert spent == pytest.approx(CAPITAL)
