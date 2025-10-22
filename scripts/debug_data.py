import pandas as pd
import numpy as np
from pathlib import Path

def inspect_csv(path):
    df = pd.read_csv(path)
    print("\nFirst few rows of raw data:")
    print(df.head())
    print("\nColumn info:")
    print(df.info())

if __name__ == "__main__":
    csv_path = "data/SM Cleaned Data MH Aggregated.csv"
    inspect_csv(csv_path)