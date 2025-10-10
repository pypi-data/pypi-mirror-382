from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def plot_series_with_smooth(df: pd.DataFrame, time_col: str, value_col: str, smooth: pd.Series):
    t = pd.to_datetime(df[time_col]) if time_col in df.columns else range(len(df))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t, df[value_col], label=value_col)
    ax.plot(t, smooth, label="smoothed")
    ax.set_title("Series vs. Smoothed")
    ax.set_xlabel(time_col)
    ax.set_ylabel(value_col)
    ax.grid(True); ax.legend()
    return fig, ax

def save_fig(fig, out_path: str | Path, dpi: int = 150):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight", dpi=dpi)
