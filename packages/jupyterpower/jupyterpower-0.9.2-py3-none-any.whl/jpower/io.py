from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

def load_csv(path: str | Path, create_placeholder: bool = False) -> pd.DataFrame:
    path = Path(path)
    if not path.exists() and create_placeholder:
        rng = np.random.default_rng(42)
        t = pd.date_range("2025-01-01", periods=50, freq="D")
        sig = np.sin(np.linspace(0, 8*np.pi, 50)) + 0.1 * rng.standard_normal(50)
        grp = rng.choice(["A", "B"], size=50)
        df = pd.DataFrame({"time": t, "signal": sig, "group": grp})
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    return pd.read_csv(path)
