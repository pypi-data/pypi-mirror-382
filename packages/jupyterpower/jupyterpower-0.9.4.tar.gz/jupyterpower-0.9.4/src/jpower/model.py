# src/jpower/model.py
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def fit_linear_time(df: pd.DataFrame, time_col: str = "time", y_col: str | None = "signal"):
    if time_col in df.columns:
        t = pd.to_datetime(df[time_col], errors="coerce")
        X = (t - t.min()).dt.days.values.reshape(-1, 1)
    else:
        X = np.arange(len(df)).reshape(-1, 1)

    if y_col is None or y_col not in df.columns:
        nums = df.select_dtypes(include="number").columns
        if len(nums) == 0:
            raise ValueError("No numeric columns available for y.")
        y_col = nums[-1]

    # y = pd.to_numeric(df[y_col], errors="coerce").fillna(method="ffill").fillna(method="bfill").values
    y = pd.to_numeric(df[y_col], errors="coerce").ffill().bfill().values
    m = LinearRegression().fit(X, y)
    pred = m.predict(X)
    return m, X, y, pred
