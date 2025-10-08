import numpy as np
import pandas as pd
from jpower.model import fit_linear_time

def test_fit_linear_time_with_time_col():
    n = 50
    t = pd.date_range("2025-01-01", periods=n, freq="D")
    # y = 0.5 * day + noise
    X_true = np.arange(n).reshape(-1, 1)
    y_true = 0.5 * X_true.ravel()
    rng = np.random.default_rng(42)
    y = y_true + rng.normal(scale=0.1, size=n)

    df = pd.DataFrame({"time": t, "signal": y})
    m, X, y_vec, pred = fit_linear_time(df, time_col="time", y_col="signal")

    assert X.shape == (n, 1)
    assert len(y_vec) == n and len(pred) == n
    # slope close to 0.5
    assert abs(m.coef_[0] - 0.5) < 0.1
    # predictions correlate with truth
    corr = np.corrcoef(pred, y_true)[0,1]
    assert corr > 0.95
