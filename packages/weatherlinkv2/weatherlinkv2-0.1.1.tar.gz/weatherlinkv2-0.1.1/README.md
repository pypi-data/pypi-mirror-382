# WeatherLink v2 API Python Library

[![PyPI version](https://badge.fury.io/py/weatherlinkv2.svg)](https://badge.fury.io/py/weatherlinkv2)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![GitHub release](https://img.shields.io/github/release/Vendetta0462/weatherlinkv2.svg)](https://GitHub.com/Vendetta0462/weatherlinkv2/releases/)

A comprehensive Python library for accessing WeatherLink v2 API to retrieve meteorological and air quality data efficiently. Designed for developers, researchers, and weather enthusiasts who need fast, reliable access to weather station data.

## 🌟 Features

- **Professional API Integration**: Robust authentication and data retrieval
- **Flexible Operation Modes**: Choose between demo mode (testing/education) or production mode (your stations)
- **Sensor-Specific Processing**: Support for different sensor types with automatic field mapping
- **Automatic Request Chunking**: Historical data requests > 24 hours automatically split and combined
- **Multiple Sensor Support**: Vantage Pro2, Vantage Vue, and AirLink sensors
- **Comprehensive Data Processing**: Automatic unit conversions (Imperial ↔ Metric)
- **Advanced Visualization**: Built-in plotting functions for weather data analysis
- **Export Capabilities**: CSV export with customizable formats
- **Production Ready**: Error handling, validation, and professional-grade code structure

## 🚀 Quick Start

### Installation

```bash
pip install weatherlinkv2
```

Or install from source:

```bash
git clone https://github.com/Vendetta0462/weatherlinkv2.git
cd weatherlinkv2
pip install -e .
```

### Basic Usage

#### Demo Mode (Testing/Education)
```python
from weatherlinkv2 import WeatherLinkAPI, parse_weather_data

# Initialize API in demo mode for testing
api = WeatherLinkAPI(api_key="your_api_key", api_secret="your_api_secret", demo_mode=True)

# Get current weather data from demo station
current_data = api.get_current_data()
print(f"Current sensors: {len(current_data.get('sensors', []))}")

# Get historical data (limited to 24 hours in demo mode)
historic_data = api.get_historic_data(hours_back=24)

# Parse data for specific sensor type (e.g., AirLink sensor type 323)
df = parse_weather_data(historic_data, sensor_type=323, data_structure_type=17)
print(f"Retrieved {len(df)} air quality records")
```

#### Production Mode (Your Stations)
```python
# Initialize API for production use
api = WeatherLinkAPI(api_key="your_api_key", api_secret="your_api_secret", demo_mode=False)

# Get your stations and sensors
stations = api.get_stations()
sensors = api.get_sensors()
my_station_id = stations[0]['station_id_uuid']

# Get specific station information
station_info = api.get_station_info(my_station_id)
print(f"Station: {station_info.get('station_name')}")

# Get sensor information by sensor ID (lsid)
if sensors:
    sensor_info = api.get_sensors_info(sensors[0]['lsid'])
    print(f"Sensor type: {sensor_info.get('sensor_type')}")

# Get historical data with extended range for production
# Automatically splits requests > 24h into multiple chunks
historic_data = api.get_historic_data(station_id=my_station_id, hours_back=168)  # 7 days

# Parse data for different sensor types:
# Vantage Pro2 (type 23)
df_pro2 = parse_weather_data(historic_data, sensor_type=23, data_structure_type=4)

# Vantage Vue (type 37)
df_vue = parse_weather_data(historic_data, sensor_type=37, data_structure_type=24)

# AirLink (type 323)
df_airlink = parse_weather_data(historic_data, sensor_type=323, data_structure_type=17)

print(f"Retrieved {len(df_pro2)} weather records")
```

## 📋 Requirements

- Python 3.7+
- WeatherLink API credentials (API Key + Secret)
- Internet connection

### Dependencies

- `requests` - HTTP requests
- `pandas` - Data manipulation
- `matplotlib` - Basic plotting
- `seaborn` - Enhanced visualizations
- `python-dotenv` - Environment variable management

## 🔧 API Credentials Setup

1. **Get API Credentials**: Visit the WeatherLink Developer Portal to obtain your API key and secret
2. **Create `.env` file**:

```env
WEATHERLINK_API_KEY=your_api_key_here
WEATHERLINK_API_SECRET=your_api_secret_here
```

3. **Load in your code**:

```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('WEATHERLINK_API_KEY')
api_secret = os.getenv('WEATHERLINK_API_SECRET')

api = WeatherLinkAPI(api_key, api_secret)
```

## 📚 Examples

This library includes two example files to get you started:

### Basic Usage (`examples/basic_usage.py`)
Simple and direct example showing core functionality:
- API initialization with demo mode
- Getting stations and sensors
- Retrieving current and historical data
- Basic data parsing

### Sensor Types (`examples/sensor_types.py`)
Working with different sensor types:
- Exploring available sensor types
- Sensor-specific data parsing
- Vantage Pro2 weather stations (type 23)
- Vantage Vue weather stations (type 37)
- AirLink air quality sensors (type 323)
- Different data structure types

### Running Examples

In bash:

```bash
# Make sure you have your API credentials
export WEATHERLINK_API_KEY="your_api_key"
export WEATHERLINK_API_SECRET="your_api_secret"

# Run examples
python examples/basic_usage.py
python examples/sensor_types.py
```

## 🔍 API Reference

### WeatherLinkAPI Class

| Method | Description | Parameters |
|--------|-------------|------------|
| `__init__(api_key, api_secret, demo_mode)` | Initialize API client | API credentials, operation mode |
| `get_stations()` | Get available stations | None |
| `get_station_info(station_id)` | Get specific station info | Optional station ID if demo mode is enabled |
| `get_sensors()` | Get all available sensors | None |
| `get_sensors_info(sensor_id)` | Get specific sensor info | Sensor ID (lsid) |
| `get_current_data(station_id)` | Get current weather data | Station ID |
| `get_historic_data(station_id, hours_back)` | Get historical data | Station ID, hours back (automatically chunked if > 24h) |
| `test_connection()` | Test API connection | None |

### Utility Functions

| Function | Description | Parameters | Returns |
|----------|-------------|------------|---------|
| `parse_weather_data(response, sensor_type, data_structure_type)` | Parse API response to DataFrame | API response, sensor type, optional structure type | pandas.DataFrame |
| `get_weather_summary(df)` | Generate statistics summary | DataFrame | dict |
| `create_weather_plots(df)` | Create visualization plots | DataFrame | matplotlib.Figure |
| `export_to_csv(df, filename)` | Export data to CSV | DataFrame, filename | str (file path) |

### Supported Sensor Types

| Sensor Type | Description | Data Structure Types |
|-------------|-------------|----------------------|
| 23 | Vantage Pro2 (Weather Station) | 4 (Archive) |
| 37 | Vantage Vue (Weather Station) | 24 (Archive) |
| 323 | AirLink (Air Quality) | 16 (Current), 17 (Archive) |

## ⚠️ Important Notes

### Historical Data Requests

The WeatherLink API has a 24-hour limit per request. This library automatically handles longer time periods by:
- Splitting requests > 24 hours into multiple 24-hour chunks
- Combining all responses into a single unified format
- Sorting data chronologically by timestamp
- No user intervention required - completely transparent

**Example:**
```python
# This automatically splits into 7 separate API requests and combines results
historic_data = api.get_historic_data(station_id="your_id", hours_back=168)  # 7 days
```

### Data Units

The library provides both Imperial and Metric units depending on the sensor-structure pair. For a full list of the fields and units returned by the API, please refer to the official [WeatherLink v2 API Sensor Catalog](https://weatherlink.github.io/v2-api/interactive-sensor-catalog).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License** - see the [LICENSE](LICENSE) file for details.

### Key License Terms:
- ✅ **Free for non-commercial use**: Research, education, personal projects
- ✅ **Open source friendly**: Use in other open source projects
- ❌ **No commercial use**: Cannot be used in proprietary or commercial software
- 🔄 **Share-alike**: Derivatives must use the same license

For commercial licensing options, please contact the maintainers.

**Powered by WeatherLink API 🌤️ | Made with Python 🐍**
