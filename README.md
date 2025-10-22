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