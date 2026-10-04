"""กราฟสำหรับดูข้อมูลและผล backtest"""

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure


def plot_price(df: pd.DataFrame) -> Figure:
    """กราฟราคาปิด"""
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df.index, df["close"])
    ax.set_title("Close Price Over Time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    fig.autofmt_xdate()
    return fig


def plot_equity(equity_curve: pd.Series) -> None:
    """กราฟ equity + drawdown — TODO(ฉาก 2)"""
    raise NotImplementedError
