import pandas as pd
import numpy as np
from pathlib import Path

def inspect_data(csv_path):
    p = Path(csv_path)
    if not p.exists():
        print("File not found:", p)
        return
    df = pd.read_csv(p, parse_dates=[0], index_col=0)
    ser = df.select_dtypes(include=[np.number]).iloc[:, 0]
    ser.index = pd.to_datetime(ser.index).tz_localize("Asia/Kolkata", ambiguous="NaT", nonexistent="shift_forward")
    ser = ser.resample("H").sum()
    print("Range:", ser.index.min(), "->", ser.index.max())
    print("Total hours:", len(ser), "Missing:", ser.isna().sum())
    mask = (ser == 0) | ser.isna()
    arr = mask.astype(int).values
    padded = np.concatenate([[0], arr, [0]])
    diffs = np.diff(padded)
    starts = np.where(diffs == 1)[0]
    ends = np.where(diffs == -1)[0]
    if len(starts):
        for s, e in zip(starts, ends):
            print("Zero/missing run:", ser.index[s], "->", ser.index[e-1], "hours=", e-s)
    else:
        print("No zero/missing runs found.")

if __name__ == "__main__":
    inspect_data("data/SM Cleaned Data MH Aggregated.csv")