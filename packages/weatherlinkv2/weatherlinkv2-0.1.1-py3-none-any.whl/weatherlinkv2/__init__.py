"""
WeatherLink v2 API Python Library

A comprehensive Python library for accessing WeatherLink v2 API to retrieve 
meteorological and air quality data efficiently. Designed for developers and 
researchers who need fast, reliable access to weather station data.

Features:
- Full WeatherLink v2 API integration
- Optional demo mode for testing and education
- Comprehensive data processing and visualization utilities
- Professional-grade error handling and validation
- Unit conversion support (Imperial ↔ Metric)
- Export capabilities (CSV, visualization)

Author: WeatherLink v2 Community
Version: 1.0.0
"""

from .api import WeatherLinkAPI
from .utils import parse_weather_data, get_weather_summary, export_to_csv, create_weather_plots

__version__ = "1.0.0"
__author__ = "WeatherLink v2 Community"
__description__ = "Professional Python library for WeatherLink v2 API integration"

__all__ = [
    "WeatherLinkAPI",
    "parse_weather_data", 
    "get_weather_summary",
    "export_to_csv",
    "create_weather_plots"
]
