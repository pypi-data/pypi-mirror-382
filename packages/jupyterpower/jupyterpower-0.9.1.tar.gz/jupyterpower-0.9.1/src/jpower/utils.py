from __future__ import annotations
import pandas as pd

def moving_average(df: pd.DataFrame, value_col: str | None = None, window: int = 7) -> pd.Series:
    """
    Centered moving average on a numeric column (auto-detects if not provided).
    Returns a pandas Series aligned to df.index.
    """
    if value_col is None:
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) == 0:
            raise ValueError("No numeric columns found in DataFrame.")
        value_col = numeric_cols[-1]  # pick the last numeric by default

    if value_col not in df.columns:
        raise KeyError(f"{value_col!r} not in columns: {list(df.columns)}")

    # Coerce to numeric (in case it's stringified numbers); don't mutate df
    s = pd.to_numeric(df[value_col], errors="coerce")
    if s.notna().sum() == 0:
        raise TypeError(f"Selected column {value_col!r} has no numeric values after coercion.")
    return s.rolling(window=window, center=True, min_periods=1).mean()
