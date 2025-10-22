# src/features.py
"""
Feature engineering for hourly series.
Exports:
    make_features_from_series(series, include_temp=None)
- series: pd.Series indexed by hourly timestamps (timezone-aware or naive)
- include_temp: optional pd.Series of hourly temperature values aligned to the same index
Returns:
    pd.DataFrame with a 'y' column (target) and feature columns
Notes:
- Produces lag_1, lag_2, lag_3, rolling_24 (mean of previous 24 hours),
  sin_hour, cos_hour, dayofweek, is_weekend.
- Drops rows with NaNs created by lag/rolling. Caller should ensure enough history exists.
"""

import pandas as pd
import numpy as np

def make_features_from_series(series: pd.Series, include_temp: pd.Series = None) -> pd.DataFrame:
    """
    Compact feature set:
    - hour sin/cos
    - day_of_week (one column)
    - lags 1,2,3 hours
    - 24h rolling mean
    - optional temperature series aligned to series.index
    """
    # Basic checks
    if not isinstance(series, pd.Series):
        raise TypeError("series must be a pandas Series")
    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError("series.index must be a pandas DatetimeIndex (hourly)")

    X = pd.DataFrame(index=series.index)
    hours = series.index.hour
    X["hour_sin"] = np.sin(2 * np.pi * hours / 24)
    X["hour_cos"] = np.cos(2 * np.pi * hours / 24)
    X["dow"] = series.index.dayofweek
    for lag in (1, 2, 3):
        X[f"lag_{lag}"] = series.shift(lag)
    X["roll_24h"] = series.rolling(24, min_periods=1).mean()
    if include_temp is not None:
        temp = include_temp.reindex(series.index)
        X["temp"] = temp
        X["temp_12h"] = temp.rolling(12, min_periods=1).mean()

    # Drop rows with NaN (created by lags)
    df = df.dropna()

    # Final sanity: ensure there is a 'y' column and at least one row
    if 'y' not in df.columns or len(df) == 0:
        raise ValueError("Feature dataframe is empty after dropping NaNs. Ensure series has enough history (>24 hours).")

    return X
