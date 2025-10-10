import pandas as pd
from jpower.utils import moving_average

def test_moving_average_basic():
    df = pd.DataFrame({"value": [1, 2, 3, 4, 5]})
    s = moving_average(df, "value", window=3)
    assert len(s) == 5
    assert s.isna().sum() == 0
    # center point of first 3 values
    assert abs(s.iloc[2] - (2+3+4)/3) < 1e-9

def test_moving_average_auto_detect_numeric():
    df = pd.DataFrame({"time": ["a","b","c"], "value": [10, 20, 30], "group": ["A","B","A"]})
    s = moving_average(df, None, window=2)
    assert len(s) == 3
