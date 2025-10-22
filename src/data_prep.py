import pandas as pd
import numpy as np
from pathlib import Path

def load_aggregated_csv(path):
    """Locate CSV, detect the datetime column, return first numeric series with tz-aware hourly index."""
    candidates = [Path(path), Path("data") / Path(path).name, Path("data") / str(path)]
    for p in candidates:
        if not p.exists():
            continue
        df = pd.read_csv(p)  # read raw so we can detect which column is datetime-like

        # find the column that best parses to datetimes
        best_col = None
        best_count = 0
        best_parsed = None
        for col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            count = int(parsed.notna().sum())
            if count > best_count:
                best_count = count
                best_col = col
                best_parsed = parsed

        if best_col is None or best_count == 0:
            raise ValueError(f"No datetime-like column found in {p}. Columns: {list(df.columns)}")

        # set index to detected datetime column
        df.index = best_parsed
        # drop the original datetime column if it is still present as data
        if best_col in df.columns:
            df = df.drop(columns=[best_col])

        # pick the first numeric column as the target series
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(num_cols) == 0:
            raise ValueError(f"No numeric columns found in {p} after removing datetime column.")
        ser = df[num_cols[0]].copy()
        ser.index = pd.to_datetime(ser.index)  # ensure dtype

        # ensure timezone-aware index (IST)
        try:
            if ser.index.tz is None:
                ser.index = ser.index.tz_localize("Asia/Kolkata", ambiguous="NaT", nonexistent="shift_forward")
            else:
                ser.index = ser.index.tz_convert("Asia/Kolkata")
        except Exception:
            # fallback: localize without special rules
            ser.index = ser.index.tz_localize("Asia/Kolkata", ambiguous="NaT", nonexistent="shift_forward")

        return ser

    raise FileNotFoundError(f"Aggregated CSV not found. Tried paths:\n" + "\n".join(str(p) for p in candidates))

# helpers
def _longest_consecutive_run_bool(mask):
    if len(mask) == 0:
        return 0
    arr = np.asarray(mask, dtype=int)
    padded = np.concatenate([[0], arr, [0]])
    diffs = np.diff(padded)
    starts = np.where(diffs == 1)[0]
    ends = np.where(diffs == -1)[0]
    if len(starts) == 0:
        return 0
    lengths = ends - starts
    return int(lengths.max())

def _pct_missing(series):
    total = len(series)
    if total == 0:
        return 1.0
    return float(series.isna().sum()) / float(total)

def impute_gaps(series, max_linear=2, max_ffill=24):
    s = series.copy()
    s = s.interpolate(method="time", limit=max_linear)
    s = s.ffill(limit=max_ffill)
    s = s.bfill(limit=4)  # small backfill if leading NaNs
    return s

def cap_outliers(series, low_pct=1, high_pct=99):
    clean = series.dropna()
    if len(clean) == 0:
        return series, {"low": 0.0, "high": 0.0}
    low, high = np.percentile(clean, [low_pct, high_pct])
    return series.clip(lower=low, upper=high), {"low": float(low), "high": float(high)}

def prepare_hourly_from_aggregated(path,
                                   max_missing_pct=0.05,
                                   max_zero_run_hours=24,
                                   max_gap_hours=48):
    """
    Load, resample to hourly, impute small gaps, cap outliers, and run validation checks.
    Returns: (hourly_capped: pd.Series, caps: dict, audit: dict)
    Raises RuntimeError if data quality checks fail.
    """
    series = load_aggregated_csv(path)

    # resample by summing to hourly if original has finer freq
    series = series.resample("h").sum()

    # ensure continuous hourly index
    idx = pd.date_range(series.index.min(), series.index.max(), freq="h", tz=series.index.tz)
    series = series.reindex(idx)

    audit = {}
    audit["n_hours_total"] = len(series)
    audit["n_missing_before"] = int(series.isna().sum())
    audit["pct_missing_before"] = _pct_missing(series)

    imputed = impute_gaps(series)
    audit["n_missing_after_impute"] = int(imputed.isna().sum())
    audit["pct_missing_after_impute"] = _pct_missing(imputed)

    zero_mask = (imputed == 0) | (imputed.fillna(0) == 0)
    audit["longest_zero_run_hours"] = _longest_consecutive_run_bool(zero_mask)

    nan_mask = imputed.isna()
    audit["longest_nan_run_hours"] = _longest_consecutive_run_bool(nan_mask)

    if audit["pct_missing_after_impute"] > max_missing_pct:
        raise RuntimeError(f"Too many missing hours after imputation: {audit['pct_missing_after_impute']:.2%} (threshold={max_missing_pct:.2%})")
    if audit["longest_zero_run_hours"] >= max_zero_run_hours:
        raise RuntimeError(f"Detected long zero-run of {audit['longest_zero_run_hours']} hours (threshold={max_zero_run_hours}).")
    if audit["longest_nan_run_hours"] >= max_gap_hours:
        raise RuntimeError(f"Detected long missing-run of {audit['longest_nan_run_hours']} hours (threshold={max_gap_hours}).")

    capped, caps = cap_outliers(imputed)
    audit["cap_low"] = caps["low"]
    audit["cap_high"] = caps["high"]
    audit["n_hours_final"] = len(capped)

    return capped, caps, audit