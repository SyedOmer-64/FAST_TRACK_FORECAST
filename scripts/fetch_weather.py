import requests
import pandas as pd
from datetime import datetime, timedelta
import os

def fetch_weather_data(lat=28.36, lon=79.42, hours=48):  # example coords (Bareilly)
    end = datetime.utcnow()
    start = end - timedelta(hours=hours)
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m"
        f"&start={start.strftime('%Y-%m-%dT%H:%M')}"
        f"&end={end.strftime('%Y-%m-%dT%H:%M')}"
        "&timezone=Asia%2FKolkata"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    df = df.set_index("time")
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/weather_hourly.csv")
    print("Saved data/weather_hourly.csv")

if __name__ == "__main__":
    fetch_weather_data()