<<<<<<< HEAD
# Fast Track Forecast

24-hour electricity demand forecasting using smart meter data from Bareilly and Mathura.

## Features
- Hourly demand forecasting for next 24 hours
- Weather integration (optional) using Open-Meteo API
- Data quality validation and reporting
- Quantile forecasts (10th, 50th, 90th percentiles)
- Seasonal naive baseline comparison

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Windows)
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Fetch weather data (optional)
python scripts/fetch_weather.py

# Run forecast
python run_forecast.py --csv "data/SM Cleaned Data MH Aggregated.csv" --with_weather
```

## Project Structure
```
fast_track_forecast/
├── data/                    # Input data directory
├── src/                     # Source code
│   ├── data_prep.py        # Data preparation and validation
│   └── features.py         # Feature engineering
├── scripts/                 # Utility scripts
│   ├── fetch_weather.py    # Weather data fetching
│   └── inspect_data.py     # Data inspection tools
├── artifacts/              # Output files
│   └── fast_track/        
│       └── plots/         # Generated plots
├── requirements.txt        # Project dependencies
└── run_forecast.py        # Main execution script
```

## Data Sources
- Demand data: [Kaggle Smart Meter Dataset](https://www.kaggle.com/datasets/jehanbhathena/smart-meter-datamathura-and-bareilly)
- Weather data: [Open-Meteo API](https://open-meteo.com/en/docs)

## License
MIT
=======
## Description

FAST_TRACK_FORECAST is a complete end-to-end forecasting system designed for rapid deployment and reliable results.  
It automatically prepares, cleans, and forecasts hourly energy consumption data using modern data processing and machine learning techniques.

### Key Highlights
- Detects and removes long zero-runs (data outages)
- Automatically cleans and trims missing or corrupted data
- Uses Ridge Regression for accurate 24-hour forecasts
- Includes modular scripts for data preparation, cleaning, and forecasting
- Compatible with real-time data from Open-Meteo API

This project is designed for scalable energy analytics and rapid forecasting — ideal for smart grid data, metering systems, and energy research.
>>>>>>> ddf39a6187593aed83e913a2327224a9fe773931
