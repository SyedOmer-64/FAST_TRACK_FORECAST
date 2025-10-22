import argparse
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from src.data_prep import prepare_hourly_from_aggregated
from src.features import make_features_from_series

def train_models(X, y):
    models = {}
    for h in range(1, 25):
        y_h = y.shift(-h)
        df = pd.concat([X, y_h.rename("y_h")], axis=1).dropna()
        m = Ridge(alpha=1.0)
        m.fit(df.drop(columns=["y_h"]), df["y_h"])
        models[h] = m
    return models

def predict(models, feats):
    row = feats.iloc[[-1]]  # keep frame
    preds = np.array([models[h].predict(row)[0] for h in range(1,25)])
    return preds

def compute_residual_quantiles(models, X, y):
    residual_quantiles = {}
    for h in range(1,25):
        y_h = y.shift(-h)
        df = pd.concat([X, y_h.rename("y_h")], axis=1).dropna()
        if df.empty:
            residual_quantiles[h] = {"p10":0.0,"p50":0.0,"p90":0.0}
            continue
        preds_train = models[h].predict(df.drop(columns=["y_h"]))
        res = df["y_h"].values - preds_train
        residual_quantiles[h] = {
            "p10": np.quantile(res, 0.10),
            "p50": np.quantile(res, 0.50),
            "p90": np.quantile(res, 0.90),
        }
    return residual_quantiles

def main(csv, with_weather=False):
    try:
        hourly, caps, audit = prepare_hourly_from_aggregated(csv)
    except RuntimeError as e:
        print("Data quality check failed:", e)
        # build baseline-only forecast (seasonal naive last-day)
        hourly = pd.read_csv(csv, parse_dates=[0], index_col=0).iloc[:,0]
        hourly.index = pd.to_datetime(hourly.index).tz_localize("Asia/Kolkata")
        last = hourly.resample("h").sum().iloc[-24:]
        idx = pd.date_range(start=last.index[-1]+pd.Timedelta(hours=1), periods=24, freq="h", tz=last.index.tz)
        out = pd.DataFrame({"timestamp": idx, "yhat": last.values, "baseline": last.values})
        out.to_csv("artifacts/fast_track/forecast_T_plus_24.csv", index=False)
        print("Saved baseline-only forecast due to data quality issues.")
        raise SystemExit(0)

    print("Data audit:", audit)

    # optional weather merge
    temp_series = None
    if with_weather:
        try:
            w = pd.read_csv("data/weather_hourly.csv", parse_dates=["time"], index_col="time")
            temp_series = w["temperature_2m"]
            if temp_series.index.tz is None:
                temp_series.index = temp_series.index.tz_localize("Asia/Kolkata")
            temp_series = temp_series.reindex(hourly.index)
            print("Weather loaded.")
        except Exception as e:
            print("Weather not used:", e)
            temp_series = None

    feats = make_features_from_series(hourly, include_temp=temp_series)
    # align X/y (drop leading NaNs)
    joined = feats.join(hourly.rename("y"), how="inner")
    X = joined.drop(columns=["y"])
    y = joined["y"]

    models = train_models(X, y)
    residual_quantiles = compute_residual_quantiles(models, X, y)

    preds = predict(models, X)
    p10 = [preds[h-1] + residual_quantiles[h]["p10"] for h in range(1,25)]
    p50 = [preds[h-1] + residual_quantiles[h]["p50"] for h in range(1,25)]
    p90 = [preds[h-1] + residual_quantiles[h]["p90"] for h in range(1,25)]

    last_time = hourly.index[-1]
    idx = pd.date_range(start=last_time + pd.Timedelta(hours=1), periods=24, freq="H", tz=hourly.index.tz)

    # baseline seasonal naive (same hour previous day)
    baseline = [hourly.shift(24).reindex(idx).values[i] for i in range(24)]

    out = pd.DataFrame({
        "timestamp": idx,
        "yhat": preds,
        "y_p10": p10,
        "y_p50": p50,
        "y_p90": p90,
        "baseline": baseline
    })
    os.makedirs("artifacts/fast_track", exist_ok=True)
    out.to_csv("artifacts/fast_track/forecast_T_plus_24.csv", index=False)
    print("Saved artifacts/fast_track/forecast_T_plus_24.csv")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/SM Cleaned Data MH Aggregated.csv")
    parser.add_argument("--with_weather", action="store_true")
    args = parser.parse_args()
    main(args.csv, with_weather=args.with_weather)