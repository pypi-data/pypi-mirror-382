"""
Unit tests for WeatherLink v2 API Library

Basic test suite for the weatherlinkv2 library components.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to sys.path to import the library
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weatherlinkv2.api import WeatherLinkAPI
from weatherlinkv2.utils import parse_weather_data, get_weather_summary, export_to_csv


class TestWeatherLinkAPI:
    """Test cases for WeatherLinkAPI class"""
    
    def test_init_valid_credentials(self):
        """Test API initialization with valid credentials"""
        api = WeatherLinkAPI("test_key", "test_secret")
        assert api.api_key == "test_key"
        assert api.api_secret == "test_secret"
        assert api.base_url == "https://api.weatherlink.com/v2"
        assert api.demo_station_id == "9722cfc3-a4ef-47b9-befb-72f52592d6ed"
        assert api.demo_mode is False
    
    def test_init_demo_mode(self):
        """Test API initialization with demo mode"""
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        assert api.demo_mode is True
    
    def test_init_invalid_credentials(self):
        """Test API initialization with invalid credentials"""
        with pytest.raises(ValueError):
            WeatherLinkAPI("", "test_secret")
        
        with pytest.raises(ValueError):
            WeatherLinkAPI("test_key", "")
        
        with pytest.raises(ValueError):
            WeatherLinkAPI(None, None)
    
    @patch('weatherlinkv2.api.requests.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        result = api._make_request("test_endpoint")
        
        assert result == {"test": "data"}
        mock_get.assert_called_once()
    
    @patch('weatherlinkv2.api.requests.get')
    def test_get_stations_success(self, mock_get):
        """Test getting stations successfully"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "stations": [
                {"station_id": "123", "station_name": "Test Station"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        stations = api.get_stations()
        
        assert len(stations) == 1
        assert stations[0]["station_name"] == "Test Station"
    
    @patch('weatherlinkv2.api.requests.get')
    def test_get_current_data_success(self, mock_get):
        """Test getting current data successfully"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "sensors": [
                {"data": [{"temp": 25.5, "hum": 60}]}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Use demo mode to avoid needing station_id
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        current = api.get_current_data()
        
        assert "sensors" in current
        assert len(current["sensors"]) == 1
    
    @patch('weatherlinkv2.api.requests.get')
    def test_get_sensors_success(self, mock_get):
        """Test getting sensors successfully"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "sensors": [
                {"lsid": "12345", "sensor_type": 323, "product_name": "AirLink"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        sensors = api.get_sensors()
        
        assert len(sensors) == 1
        assert sensors[0]["sensor_type"] == 323
        assert sensors[0]["lsid"] == "12345"
    
    @patch('weatherlinkv2.api.requests.get')
    def test_get_sensors_info_success(self, mock_get):
        """Test getting specific sensor info successfully"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "sensors": [
                {"lsid": "12345", "sensor_type": 323, "product_name": "AirLink", "active": True}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        sensor_info = api.get_sensors_info("12345")
        
        assert sensor_info["lsid"] == "12345"
        assert sensor_info["sensor_type"] == 323
        assert sensor_info["active"] is True
    
    @patch('weatherlinkv2.api.requests.get')
    def test_get_station_info_success(self, mock_get):
        """Test getting specific station info using direct endpoint"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "stations": [
                {"station_id_uuid": "test-uuid", "station_name": "Test Station", "active": True}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        station_info = api.get_station_info("test-uuid")
        
        assert station_info["station_id_uuid"] == "test-uuid"
        assert station_info["station_name"] == "Test Station"
        assert station_info["active"] is True


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_parse_weather_data_empty_response(self):
        """Test parsing empty API response"""
        empty_response = {"sensors": []}
        df = parse_weather_data(empty_response, sensor_type=23)
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    
    def test_parse_weather_data_valid_response(self):
        """Test parsing valid API response for standard weather station"""
        valid_response = {
            "sensors": [
                {
                    "sensor_type": 23,
                    "data": [
                        {
                            "ts": 1640995200,  # 2022-01-01 00:00:00 UTC
                            "temp": 72.5,
                            "hum": 65,
                            "bar": 30.12,
                            "wind_speed_avg": 10.5
                        }
                    ]
                }
            ]
        }
        
        df = parse_weather_data(valid_response, sensor_type=23)
        
        assert not df.empty
        assert len(df) == 1
        assert isinstance(df.index, pd.DatetimeIndex)  # Check datetime index
        assert "temperature_f" in df.columns
        assert "temperature_c" in df.columns
        assert "humidity_pct" in df.columns
        
        # Check unit conversions
        temp_c = (72.5 - 32) * 5/9
        assert abs(df.iloc[0]["temperature_c"] - temp_c) < 0.1
    
    def test_parse_weather_data_airlink_sensor(self):
        """Test parsing AirLink sensor data (type 323)"""
        airlink_response = {
            "sensors": [
                {
                    "sensor_type": 323,
                    "data": [
                        {
                            "ts": 1640995200,
                            "temp": 75.0,
                            "hum": 60,
                            "pm_2p5": 12.5,
                            "pm_10": 15.0,
                            "aqi_val": 45
                        }
                    ]
                }
            ]
        }
        
        df = parse_weather_data(airlink_response, sensor_type=323, data_structure_type=16)
        
        assert not df.empty
        assert len(df) == 1
        assert "temperature_f" in df.columns
        assert "pm25_ugm3" in df.columns
        assert "pm10_ugm3" in df.columns
        assert "aqi_value" in df.columns
        
        # Check specific values
        assert df.iloc[0]["pm25_ugm3"] == 12.5
        assert df.iloc[0]["aqi_value"] == 45
    
    def test_parse_weather_data_wrong_sensor_type(self):
        """Test parsing when no matching sensor type is found"""
        response = {
            "sensors": [
                {
                    "sensor_type": 999,  # Non-existent sensor type
                    "data": [{"ts": 1640995200, "temp": 72.5}]
                }
            ]
        }
        
        df = parse_weather_data(response, sensor_type=23)  # Looking for type 23
        
        assert df.empty  # Should be empty since no sensor type 23 found
    
    def test_get_weather_summary_empty_dataframe(self):
        """Test weather summary with empty DataFrame"""
        empty_df = pd.DataFrame()
        summary = get_weather_summary(empty_df)
        
        assert summary == {}
    
    def test_get_weather_summary_valid_dataframe(self):
        """Test weather summary with valid DataFrame"""
        # Create sample data with datetime index
        timestamps = [datetime.now() - timedelta(hours=1), datetime.now()]
        data = {
            "temperature_c": [20.0, 25.0],
            "humidity_pct": [60.0, 70.0],
            "wind_speed_ms": [2.0, 3.0]
        }
        df = pd.DataFrame(data, index=pd.DatetimeIndex(timestamps))
        
        summary = get_weather_summary(df)
        
        assert "time_range" in summary
        assert "temperature" in summary
        assert "humidity" in summary
        assert "wind" in summary
        
        # Check calculations
        assert summary["temperature"]["mean"] == 22.5
        assert summary["temperature"]["min"] == 20.0
        assert summary["temperature"]["max"] == 25.0
    
    def test_export_to_csv(self, tmp_path):
        """Test CSV export functionality"""
        # Create sample data with datetime index
        timestamps = [datetime.now()]
        data = {
            "temperature_c": [22.5],
            "temperature_f": [72.5],
            "humidity_pct": [65.0]
        }
        df = pd.DataFrame(data, index=pd.DatetimeIndex(timestamps))
        
        # Test export
        csv_file = tmp_path / "test_weather.csv"
        result_path = export_to_csv(df, str(csv_file))
        
        assert os.path.exists(result_path)
        
        # Read back and verify
        df_read = pd.read_csv(result_path)
        assert len(df_read) == 1
        assert "temperature_c" in df_read.columns


class TestDataProcessing:
    """Test cases for data processing functions"""
    
    def test_unit_conversions(self):
        """Test unit conversion accuracy"""
        # Test temperature conversion
        temp_f = 72.5
        expected_temp_c = (temp_f - 32) * 5/9
        
        response = {
            "sensors": [
                {
                    "sensor_type": 23,
                    "data": [{"ts": 1640995200, "temp": temp_f}]
                }
            ]
        }
        
        df = parse_weather_data(response, sensor_type=23)
        actual_temp_c = df.iloc[0]["temperature_c"]
        
        assert abs(actual_temp_c - expected_temp_c) < 0.001
        
        # Test wind speed conversion
        wind_mph = 10.0
        expected_wind_ms = wind_mph * 0.44704
        
        response = {
            "sensors": [
                {
                    "sensor_type": 23,
                    "data": [{"ts": 1640995200, "wind_speed_avg": wind_mph}]
                }
            ]
        }
        
        df = parse_weather_data(response, sensor_type=23)
        actual_wind_ms = df.iloc[0]["wind_speed_ms"]
        
        assert abs(actual_wind_ms - expected_wind_ms) < 0.001


def test_library_imports():
    """Test that all main components can be imported"""
    from weatherlinkv2 import WeatherLinkAPI, parse_weather_data, export_to_csv, create_weather_plots
    
    # Test that classes and functions exist
    assert WeatherLinkAPI is not None
    assert parse_weather_data is not None
    assert export_to_csv is not None
    assert create_weather_plots is not None


class TestSensorSpecificProcessing:
    """Test cases for sensor-specific data processing"""
    
    def test_airlink_current_conditions(self):
        """Test AirLink current conditions parsing (structure 16)"""
        response = {
            "sensors": [
                {
                    "sensor_type": 323,
                    "data": [
                        {
                            "ts": 1640995200,
                            "temp": 75.0,
                            "hum": 60,
                            "pm_2p5": 12.5,
                            "pm_2p5_1_hour": 13.0,
                            "pm_10": 15.0,
                            "aqi_val": 45,
                            "aqi_desc": "Good"
                        }
                    ]
                }
            ]
        }
        
        df = parse_weather_data(response, sensor_type=323, data_structure_type=16)
        
        assert not df.empty
        assert "temperature_f" in df.columns
        assert "pm25_ugm3" in df.columns
        assert "pm25_1h_ugm3" in df.columns
        assert "aqi_value" in df.columns
        assert "aqi_description" in df.columns
        
        # Check specific mappings
        assert df.iloc[0]["pm25_ugm3"] == 12.5
        assert df.iloc[0]["pm25_1h_ugm3"] == 13.0
        assert df.iloc[0]["aqi_description"] == "Good"
    
    def test_airlink_archive_records(self):
        """Test AirLink archive records parsing (structure 17)"""
        response = {
            "sensors": [
                {
                    "sensor_type": 323,
                    "data": [
                        {
                            "ts": 1640995200,
                            "temp_avg": 75.0,
                            "temp_hi": 78.0,
                            "temp_lo": 72.0,
                            "hum_last": 60,
                            "pm_2p5_avg": 12.5,
                            "pm_2p5_hi": 15.0,
                            "aqi_avg_val": 45
                        }
                    ]
                }
            ]
        }
        
        df = parse_weather_data(response, sensor_type=323, data_structure_type=17)
        
        assert not df.empty
        assert "temperature_f" in df.columns
        assert "temperature_max_f" in df.columns
        assert "temperature_min_f" in df.columns
        assert "pm25_ugm3" in df.columns
        assert "pm25_max_ugm3" in df.columns
        assert "aqi_value" in df.columns
        
        # Check specific mappings
        assert df.iloc[0]["temperature_f"] == 75.0
        assert df.iloc[0]["temperature_max_f"] == 78.0
        assert df.iloc[0]["pm25_max_ugm3"] == 15.0
    
    def test_generic_sensor_fallback(self):
        """Test generic field mapping when specific sensor type not recognized"""
        response = {
            "sensors": [
                {
                    "sensor_type": 999,  # Unknown sensor type
                    "data": [
                        {
                            "ts": 1640995200,
                            "temp_out": 75.0,
                            "hum_out": 60,
                            "custom_field": 123
                        }
                    ]
                }
            ]
        }
        
        df = parse_weather_data(response, sensor_type=999)
        
        assert not df.empty
        assert "temperature_f" in df.columns  # Generic mapping should work
        assert "humidity_pct" in df.columns
        assert "custom_field" in df.columns  # Unknown fields preserved
        
        assert df.iloc[0]["temperature_f"] == 75.0
        assert df.iloc[0]["custom_field"] == 123
    
    def test_empty_columns_removal(self):
        """Test that columns with all None values are removed"""
        response = {
            "sensors": [
                {
                    "sensor_type": 23,
                    "data": [
                        {
                            "ts": 1640995200,
                            "temp": 75.0,
                            "missing_field": None,
                            "another_missing": None
                        },
                        {
                            "ts": 1640998800,
                            "temp": 76.0,
                            "missing_field": None,
                            "another_missing": None
                        }
                    ]
                }
            ]
        }
        
        df = parse_weather_data(response, sensor_type=23)
        
        assert not df.empty
        assert "temperature_f" in df.columns
        assert "missing_field" not in df.columns  # Should be removed
        assert "another_missing" not in df.columns  # Should be removed


class TestAPIEndpoints:
    """Test API endpoint construction and parameter handling"""
    
    @patch('weatherlinkv2.api.requests.get')
    def test_demo_mode_parameter(self, mock_get):
        """Test that demo parameter is added in demo mode"""
        mock_response = Mock()
        mock_response.json.return_value = {"stations": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test demo mode
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        api.get_stations()
        
        # Check that demo parameter was added
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert 'demo' in params
        assert params['demo'] == 'true'
    
    @patch('weatherlinkv2.api.requests.get')
    def test_production_mode_no_demo_param(self, mock_get):
        """Test that demo parameter is not added in production mode"""
        mock_response = Mock()
        mock_response.json.return_value = {"stations": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test production mode
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=False)
        api.get_stations()
        
        # Check that demo parameter was not added
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert 'demo' not in params
    
    @patch('weatherlinkv2.api.requests.get')
    def test_direct_endpoint_calls(self, mock_get):
        """Test that new API methods use direct endpoints"""
        mock_response = Mock()
        mock_response.json.return_value = {
            "stations": [{"station_id_uuid": "test-id", "station_name": "Test"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WeatherLinkAPI("test_key", "test_secret", demo_mode=True)
        api.get_station_info("test-station-id")
        
        # Check that direct endpoint was called
        call_args = mock_get.call_args
        url = call_args[0][0]
        assert "stations/test-station-id" in url


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
