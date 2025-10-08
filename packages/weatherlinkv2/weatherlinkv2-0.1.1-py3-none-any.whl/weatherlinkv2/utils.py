"""
WeatherLink Data Processing Utilities

Utility functions for parsing, processing, and visualizing WeatherLink API data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def parse_weather_data(api_response: Dict, sensor_type: int, data_structure_type: Optional[int] = None) -> pd.DataFrame:
    """
    Parse WeatherLink API response into a pandas DataFrame for specific sensor types.
    
    This function takes the raw JSON response from the WeatherLink API and converts
    it into a structured DataFrame with standardized column names and units based
    on the sensor type and data structure.
    
    Args:
        api_response (dict): Raw API response from WeatherLink
        sensor_type (int): Sensor type to filter and parse (e.g., 323 for AirLink)
        data_structure_type (int, optional): Data structure type for specific parsing
        
    Returns:
        pd.DataFrame: Processed weather data with standardized columns and datetime index
        
    Example:
        >>> historic_data = api.get_historic_data()
        >>> df = parse_weather_data(historic_data, sensor_type=323, data_structure_type=17)
        >>> print(df.columns.tolist())
    """
    
    records = []
    
    # Define sensor-specific field mappings
    sensor_field_mappings = {
        323: {  # AirLink sensor
            16: {  # Current conditions
                'temp': 'temperature_f',
                'hum': 'humidity_pct',
                'dew_point': 'dew_point_f',
                'wet_bulb': 'wet_bulb_f',
                'heat_index': 'heat_index_f',
                'pm_1': 'pm1_ugm3',
                'pm_2p5': 'pm25_ugm3',
                'pm_2p5_1_hour': 'pm25_1h_ugm3',
                'pm_2p5_3_hour': 'pm25_3h_ugm3',
                'pm_2p5_nowcast': 'pm25_nowcast_ugm3',
                'pm_2p5_24_hour': 'pm25_24h_ugm3',
                'pm_10': 'pm10_ugm3',
                'pm_10_1_hour': 'pm10_1h_ugm3',
                'pm_10_3_hour': 'pm10_3h_ugm3',
                'pm_10_nowcast': 'pm10_nowcast_ugm3',
                'pm_10_24_hour': 'pm10_24h_ugm3',
                'aqi_val': 'aqi_value',
                'aqi_desc': 'aqi_description',
                'aqi_1_hour_val': 'aqi_1h_value',
                'aqi_1_hour_desc': 'aqi_1h_description',
                'aqi_nowcast_val': 'aqi_nowcast_value',
                'aqi_nowcast_desc': 'aqi_nowcast_description'
            },
            17: {  # Archive records
                'temp_avg': 'temperature_f',
                'temp_hi': 'temperature_max_f',
                'temp_lo': 'temperature_min_f',
                'hum_last': 'humidity_pct',
                'hum_hi': 'humidity_max_pct',
                'hum_lo': 'humidity_min_pct',
                'dew_point_last': 'dew_point_f',
                'dew_point_hi': 'dew_point_max_f',
                'dew_point_lo': 'dew_point_min_f',
                'wet_bulb_last': 'wet_bulb_f',
                'wet_bulb_hi': 'wet_bulb_max_f',
                'wet_bulb_lo': 'wet_bulb_min_f',
                'heat_index_last': 'heat_index_f',
                'heat_index_hi': 'heat_index_max_f',
                'pm_1_avg': 'pm1_ugm3',
                'pm_1_hi': 'pm1_max_ugm3',
                'pm_2p5_avg': 'pm25_ugm3',
                'pm_2p5_hi': 'pm25_max_ugm3',
                'pm_10_avg': 'pm10_ugm3',
                'pm_10_hi': 'pm10_max_ugm3',
                'aqi_avg_val': 'aqi_value',
                'aqi_avg_desc': 'aqi_description',
                'aqi_hi_val': 'aqi_max_value',
                'aqi_hi_desc': 'aqi_max_description'
            }
        },
        23: {  # Vantage Pro2 weather station
            4: {  # WeatherLink IP/Vantage Connect Archive Record - Revision B
                # Temperature
                'temp_out': 'temperature_out_f',
                'temp_out_hi': 'temperature_out_max_f',
                'temp_out_lo': 'temperature_out_min_f',
                'temp_in': 'temperature_in_f',
                # Humidity
                'hum_in': 'humidity_in_pct',
                'hum_out': 'humidity_out_pct',
                # Rainfall
                'rainfall_in': 'rainfall_in',
                'rainfall_mm': 'rainfall_mm',
                'rain_rate_hi_in': 'rain_rate_max_in',
                'rain_rate_hi_mm': 'rain_rate_max_mm',
                # Pressure
                'bar': 'pressure_in',
                'abs_press': 'pressure_absolute_in',
                'bar_noaa': 'pressure_sealevel_in',
                # Solar Radiation
                'solar_rad_avg': 'solar_radiation_wm2',
                'solar_rad_hi': 'solar_radiation_max_wm2',
                'uv_index_avg': 'uv_index',
                'uv_index_hi': 'uv_index_max',
                # Wind
                'wind_speed_avg': 'wind_speed_mph',
                'wind_speed_hi': 'wind_speed_max_mph',
                'wind_dir_of_hi': 'wind_dir_at_max',
                'wind_dir_of_prevail': 'wind_dir_prevail',
                'wind_chill': 'wind_chill_f'
            }
        },
        37: {  # Vantage Vue weather station
            24: {  # WeatherLink Console ISS Archive Record
                # Temperature
                'temp_last': 'temperature_f',
                'temp_avg': 'temperature_avg_f',
                'temp_hi': 'temperature_max_f',
                'temp_lo': 'temperature_min_f',
                # Humidity
                'hum_last': 'humidity_pct',
                'hum_hi': 'humidity_max_pct',
                'hum_lo': 'humidity_min_pct',
                # Rainfall
                'rainfall_in': 'rainfall_in',
                'rainfall_mm': 'rainfall_mm',
                'rain_rate_hi_in': 'rain_rate_max_in',
                'rain_rate_hi_mm': 'rain_rate_max_mm',
                # Solar Radiation
                'solar_rad_avg': 'solar_radiation_wm2',
                'solar_rad_hi': 'solar_radiation_max_wm2',
                'uv_index_avg': 'uv_index',
                'uv_index_hi': 'uv_index_max',
                # Wind
                'wind_speed_avg': 'wind_speed_mph',
                'wind_speed_hi': 'wind_speed_max_mph',
                'wind_speed_hi_dir': 'wind_dir_at_max_deg',
                'wind_dir_of_prevail': 'wind_dir_prevail_deg',
                'wind_dir_of_avg': 'wind_dir_avg_deg',
                'wind_chill_last': 'wind_chill_f',
                'wind_chill_lo': 'wind_chill_min_f'
            }
        }
    }
    
    # Generic field mappings for common weather station data
    generic_mappings = {
        'temp_out': 'temperature_f',
        'temp': 'temperature_f',
        'hum_out': 'humidity_pct',
        'hum': 'humidity_pct',
        'bar': 'pressure_in',
        'wind_speed_avg': 'wind_speed_mph',
        'wind_dir_avg': 'wind_dir_deg',
        'rainfall_in': 'rainfall_in',
        'pm_2p5': 'pm25_ugm3',
        'pm_10': 'pm10_ugm3',
        'solar_rad': 'solar_rad',
        'uv_index': 'uv_index',
        'dew_point': 'dew_point_f',
        'heat_index': 'heat_index_f',
        'wind_chill': 'wind_chill_f',
        'feels_like': 'feels_like_f'
    }
    
    for sensor in api_response.get('sensors', []):
        # Filter by sensor type
        if sensor.get('sensor_type') != sensor_type:
            continue
            
        if 'data' not in sensor:
            continue
            
        sensor_data = sensor['data']
        if not isinstance(sensor_data, list):
            sensor_data = [sensor_data]
            
        for record in sensor_data:
            if 'ts' not in record:
                continue
            
            parsed_record = {'timestamp': pd.to_datetime(record['ts'], unit='s')}
            
            # Use specific mapping if available
            field_mapping = None
            if (sensor_type in sensor_field_mappings and 
                data_structure_type and 
                data_structure_type in sensor_field_mappings[sensor_type]):
                field_mapping = sensor_field_mappings[sensor_type][data_structure_type]
            
            # Parse fields using specific mapping or generic mapping
            for field_name, value in record.items():
                if field_name == 'ts':
                    continue
                    
                if field_mapping and field_name in field_mapping:
                    standardized_name = field_mapping[field_name]
                    parsed_record[standardized_name] = value
                elif field_name in generic_mappings:
                    standardized_name = generic_mappings[field_name]
                    parsed_record[standardized_name] = value
                else:
                    # Keep original field name if no mapping found
                    parsed_record[field_name] = value
            
            records.append(parsed_record)
    
    df = pd.DataFrame(records)
    
    if not df.empty:
        # Set timestamp as index
        df.set_index('timestamp', inplace=True)
        df = df.sort_index()
        
        # Remove columns where all values are None
        df = df.dropna(axis=1, how='all')
        
        # Add metric conversions for temperature fields
        temp_f_columns = [col for col in df.columns if col.endswith('_f')]
        for temp_col in temp_f_columns:
            if df[temp_col].notna().any():
                metric_col = temp_col.replace('_f', '_c')
                df[metric_col] = (df[temp_col] - 32) * 5/9
        
        # Add metric conversions for other common fields
        if 'wind_speed_mph' in df.columns and df['wind_speed_mph'].notna().any():
            df['wind_speed_ms'] = df['wind_speed_mph'] * 0.44704
            df['wind_speed_kmh'] = df['wind_speed_mph'] * 1.609344
        
        if 'rainfall_in' in df.columns and df['rainfall_in'].notna().any():
            df['rainfall_mm'] = df['rainfall_in'] * 25.4
        
        if 'pressure_in' in df.columns and df['pressure_in'].notna().any():
            df['pressure_hpa'] = df['pressure_in'] * 33.8639
    
    return df


def get_weather_summary(df: pd.DataFrame) -> Dict:
    """
    Generate a summary of weather data statistics.
    
    Args:
        df (pd.DataFrame): Weather data DataFrame from parse_weather_data()
        
    Returns:
        dict: Summary statistics for various weather parameters
        
    Example:
        >>> df = parse_weather_data(historic_data, sensor_type=323)
        >>> summary = get_weather_summary(df)
        >>> print(f"Average temperature: {summary['temperature']['mean']:.1f}°C")
    """
    if df.empty:
        return {}
    
    summary = {
        'time_range': {
            'start': df.index.min(),
            'end': df.index.max(),
            'duration_hours': (df.index.max() - df.index.min()).total_seconds() / 3600,
            'data_points': len(df)
        }
    }
    
    # Temperature summary
    if 'temperature_c' in df.columns and df['temperature_c'].notna().any():
        summary['temperature'] = {
            'mean': df['temperature_c'].mean(),
            'min': df['temperature_c'].min(),
            'max': df['temperature_c'].max(),
            'std': df['temperature_c'].std()
        }
    
    # Humidity summary
    if 'humidity_pct' in df.columns and df['humidity_pct'].notna().any():
        summary['humidity'] = {
            'mean': df['humidity_pct'].mean(),
            'min': df['humidity_pct'].min(),
            'max': df['humidity_pct'].max()
        }
    
    # Wind summary
    if 'wind_speed_ms' in df.columns and df['wind_speed_ms'].notna().any():
        summary['wind'] = {
            'mean_speed_ms': df['wind_speed_ms'].mean(),
            'max_speed_ms': df['wind_speed_ms'].max(),
            'mean_direction': df['wind_dir_deg'].mean() if 'wind_dir_deg' in df.columns else None
        }
    
    # Precipitation summary
    if 'rainfall_mm' in df.columns and df['rainfall_mm'].notna().any():
        summary['precipitation'] = {
            'total_mm': df['rainfall_mm'].sum(),
            'max_rate_mm': df['rainfall_mm'].max()
        }
    
    # Air quality summary
    if 'pm25_ugm3' in df.columns and df['pm25_ugm3'].notna().any():
        summary['air_quality'] = {
            'pm25_mean': df['pm25_ugm3'].mean(),
            'pm25_max': df['pm25_ugm3'].max(),
            'pm10_mean': df['pm10_ugm3'].mean() if 'pm10_ugm3' in df.columns else None,
            'pm10_max': df['pm10_ugm3'].max() if 'pm10_ugm3' in df.columns else None
        }
    
    return summary


def export_to_csv(df: pd.DataFrame, filename: str, include_imperial: bool = False) -> str:
    """
    Export weather DataFrame to CSV file.
    
    Args:
        df (pd.DataFrame): Weather data DataFrame
        filename (str): Output filename (with or without .csv extension)
        include_imperial (bool): Whether to include imperial units
        
    Returns:
        str: Path to the exported file
        
    Example:
        >>> df = parse_weather_data(historic_data)
        >>> filepath = export_to_csv(df, "weather_data.csv")
        >>> print(f"Data exported to: {filepath}")
    """
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    # Select columns to export
    export_df = df.copy()
    
    if not include_imperial:
        # Remove imperial units, keep only metric
        imperial_cols = [col for col in export_df.columns if col.endswith('_f') or col.endswith('_in') or col.endswith('_mph')]
        export_df = export_df.drop(columns=imperial_cols, errors='ignore')
    
    export_df.to_csv(filename, index=False)
    return os.path.abspath(filename)


def create_weather_plots(df: pd.DataFrame, 
                        figsize: Tuple[int, int] = (15, 10),
                        save_path: Optional[str] = None) -> plt.Figure:
    """
    Create comprehensive weather data visualization plots.
    
    Args:
        df (pd.DataFrame): Weather data DataFrame from parse_weather_data()
        figsize (tuple): Figure size as (width, height)
        save_path (str, optional): Path to save the plot image
        
    Returns:
        matplotlib.figure.Figure: The created figure object
        
    Example:
        >>> df = parse_weather_data(historic_data, sensor_type=323)
        >>> fig = create_weather_plots(df, save_path="weather_plots.png")
        >>> plt.show()
    """
    if df.empty:
        print("No data to plot")
        return None
    
    # Set style
    plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(f'Weather Data Analysis\n{df.index.min()} to {df.index.max()}', 
                 fontsize=16, fontweight='bold')
    
    # Temperature plot
    if 'temperature_c' in df.columns and df['temperature_c'].notna().any():
        axes[0, 0].plot(df.index, df['temperature_c'], 'r-', linewidth=1.5)
        axes[0, 0].set_title('Temperature (°C)')
        axes[0, 0].set_ylabel('Temperature (°C)')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Humidity plot
    if 'humidity_pct' in df.columns and df['humidity_pct'].notna().any():
        axes[0, 1].plot(df.index, df['humidity_pct'], 'b-', linewidth=1.5)
        axes[0, 1].set_title('Humidity (%)')
        axes[0, 1].set_ylabel('Humidity (%)')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Wind speed plot
    if 'wind_speed_ms' in df.columns and df['wind_speed_ms'].notna().any():
        axes[0, 2].plot(df.index, df['wind_speed_ms'], 'g-', linewidth=1.5)
        axes[0, 2].set_title('Wind Speed (m/s)')
        axes[0, 2].set_ylabel('Wind Speed (m/s)')
        axes[0, 2].grid(True, alpha=0.3)
        axes[0, 2].tick_params(axis='x', rotation=45)
    
    # Pressure plot
    if 'pressure_hpa' in df.columns and df['pressure_hpa'].notna().any():
        axes[1, 0].plot(df.index, df['pressure_hpa'], 'purple', linewidth=1.5)
        axes[1, 0].set_title('Atmospheric Pressure (hPa)')
        axes[1, 0].set_ylabel('Pressure (hPa)')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Rainfall plot (bar chart)
    if 'rainfall_mm' in df.columns and df['rainfall_mm'].notna().any():
        non_zero_rain = df[df['rainfall_mm'] > 0]
        if not non_zero_rain.empty:
            axes[1, 1].bar(non_zero_rain.index, non_zero_rain['rainfall_mm'], 
                          color='cyan', alpha=0.7, width=0.02)
            axes[1, 1].set_title('Rainfall (mm)')
            axes[1, 1].set_ylabel('Rainfall (mm)')
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].tick_params(axis='x', rotation=45)
    
    # Air quality plot (PM2.5)
    if 'pm25_ugm3' in df.columns and df['pm25_ugm3'].notna().any():
        axes[1, 2].plot(df.index, df['pm25_ugm3'], 'orange', linewidth=1.5)
        axes[1, 2].set_title('PM2.5 (μg/m³)')
        axes[1, 2].set_ylabel('PM2.5 (μg/m³)')
        axes[1, 2].grid(True, alpha=0.3)
        axes[1, 2].tick_params(axis='x', rotation=45)
        
        # Add WHO guidelines
        axes[1, 2].axhline(y=15, color='red', linestyle='--', alpha=0.7, label='WHO 24h guideline')
        axes[1, 2].legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    
    return fig


def filter_by_time_range(df: pd.DataFrame, start_time: datetime, end_time: datetime) -> pd.DataFrame:
    """
    Filter DataFrame by time range.
    
    Args:
        df (pd.DataFrame): Weather data DataFrame
        start_time (datetime): Start time for filtering
        end_time (datetime): End time for filtering
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    return df[(df.index >= start_time) & (df.index <= end_time)].copy()


def resample_data(df: pd.DataFrame, frequency: str = '1H') -> pd.DataFrame:
    """
    Resample weather data to a different frequency.
    
    Args:
        df (pd.DataFrame): Weather data DataFrame
        frequency (str): Pandas frequency string (e.g., '1H', '30min', '1D')
        
    Returns:
        pd.DataFrame: Resampled DataFrame
    """
    if df.empty:
        return df
    
    df_resampled = df.resample(frequency).mean()
    df_resampled.reset_index(inplace=True)
    
    return df_resampled
