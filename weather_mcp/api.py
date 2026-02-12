"""
Weather API client for Open-Meteo.
Handles all weather data retrieval and processing.
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from weather_mcp.cities import get_city_info


OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


def _interpret_weather_code(code: int) -> str:
    """
    Interpret WMO weather codes into human-readable conditions.
    Based on Open-Meteo documentation.
    """
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return weather_codes.get(code, f"Unknown condition (code: {code})")


async def get_current_weather_data(city: str) -> Dict[str, Any]:
    """
    Get current weather conditions for a city.
    
    Args:
        city: City name (case-insensitive)
        
    Returns:
        Dictionary with current weather data including:
        - temperature
        - conditions
        - humidity
        - wind speed and direction
        - pressure
        - visibility
    """
    city_info = get_city_info(city)
    
    params = {
        "latitude": city_info["lat"],
        "longitude": city_info["lon"],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
            "surface_pressure",
            "precipitation"
        ],
        "timezone": "auto"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(OPEN_METEO_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    
    current = data.get("current", {})
    
    return {
        "city": city_info["name"],
        "country": city_info["country"],
        "coordinates": {
            "latitude": city_info["lat"],
            "longitude": city_info["lon"]
        },
        "timestamp": current.get("time"),
        "temperature": {
            "value": current.get("temperature_2m"),
            "unit": "°C",
            "feels_like": current.get("apparent_temperature")
        },
        "conditions": _interpret_weather_code(current.get("weather_code", 0)),
        "humidity": {
            "value": current.get("relative_humidity_2m"),
            "unit": "%"
        },
        "wind": {
            "speed": current.get("wind_speed_10m"),
            "speed_unit": "km/h",
            "direction": current.get("wind_direction_10m"),
            "direction_unit": "degrees"
        },
        "pressure": {
            "value": current.get("surface_pressure"),
            "unit": "hPa"
        },
        "precipitation": {
            "value": current.get("precipitation"),
            "unit": "mm"
        }
    }


async def get_forecast_data(city: str, days: int = 7) -> Dict[str, Any]:
    """
    Get weather forecast for a city.
    
    Args:
        city: City name (case-insensitive)
        days: Number of forecast days (1-16, default 7)
        
    Returns:
        Dictionary with forecast data for each day
    """
    if not 1 <= days <= 16:
        raise ValueError("Days must be between 1 and 16")
    
    city_info = get_city_info(city)
    
    params = {
        "latitude": city_info["lat"],
        "longitude": city_info["lon"],
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "sunrise",
            "sunset",
            "precipitation_sum",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max"
        ],
        "timezone": "auto",
        "forecast_days": days
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(OPEN_METEO_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    
    daily = data.get("daily", {})
    
    forecast_days = []
    for i in range(len(daily.get("time", []))):
        forecast_days.append({
            "date": daily["time"][i],
            "conditions": _interpret_weather_code(daily["weather_code"][i]),
            "temperature": {
                "max": daily["temperature_2m_max"][i],
                "min": daily["temperature_2m_min"][i],
                "unit": "°C"
            },
            "feels_like": {
                "max": daily["apparent_temperature_max"][i],
                "min": daily["apparent_temperature_min"][i],
                "unit": "°C"
            },
            "precipitation": {
                "total": daily["precipitation_sum"][i],
                "probability": daily["precipitation_probability_max"][i],
                "unit": "mm"
            },
            "wind": {
                "max_speed": daily["wind_speed_10m_max"][i],
                "max_gusts": daily["wind_gusts_10m_max"][i],
                "unit": "km/h"
            },
            "sun": {
                "sunrise": daily["sunrise"][i],
                "sunset": daily["sunset"][i]
            }
        })
    
    return {
        "city": city_info["name"],
        "country": city_info["country"],
        "coordinates": {
            "latitude": city_info["lat"],
            "longitude": city_info["lon"]
        },
        "forecast_days": days,
        "forecast": forecast_days
    }


async def get_weather_alerts_data(city: str) -> Dict[str, Any]:
    """
    Get weather alerts and warnings for a city.
    
    Note: Open-Meteo free API doesn't provide official weather alerts.
    This function analyzes forecast data to identify potential hazardous conditions.
    
    Args:
        city: City name (case-insensitive)
        
    Returns:
        Dictionary with potential weather alerts based on forecast analysis
    """
    city_info = get_city_info(city)
    
    # Get current and forecast data
    params = {
        "latitude": city_info["lat"],
        "longitude": city_info["lon"],
        "current": [
            "temperature_2m",
            "weather_code",
            "wind_speed_10m",
            "wind_gusts_10m",
            "precipitation"
        ],
        "hourly": [
            "temperature_2m",
            "weather_code",
            "precipitation",
            "wind_speed_10m",
            "wind_gusts_10m"
        ],
        "timezone": "auto",
        "forecast_days": 2  # Check next 48 hours
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(OPEN_METEO_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    
    alerts = []
    current = data.get("current", {})
    hourly = data.get("hourly", {})
    
    # Check current conditions
    current_wind = current.get("wind_speed_10m", 0)
    current_gusts = current.get("wind_gusts_10m", 0)
    current_temp = current.get("temperature_2m", 0)
    current_precip = current.get("precipitation", 0)
    
    # High wind alert
    if current_wind > 50 or current_gusts > 70:
        alerts.append({
            "type": "High Wind Warning",
            "severity": "moderate" if current_wind < 70 else "severe",
            "description": f"Strong winds detected: {current_wind} km/h (gusts: {current_gusts} km/h)",
            "issued_at": current.get("time")
        })
    
    # Extreme temperature alerts
    if current_temp > 35:
        alerts.append({
            "type": "Heat Advisory",
            "severity": "moderate" if current_temp < 40 else "severe",
            "description": f"High temperature: {current_temp}°C. Stay hydrated and avoid prolonged sun exposure.",
            "issued_at": current.get("time")
        })
    elif current_temp < -10:
        alerts.append({
            "type": "Cold Weather Advisory",
            "severity": "moderate" if current_temp > -20 else "severe",
            "description": f"Very cold temperature: {current_temp}°C. Dress warmly and limit outdoor exposure.",
            "issued_at": current.get("time")
        })
    
    # Heavy precipitation
    if current_precip > 10:
        alerts.append({
            "type": "Heavy Precipitation",
            "severity": "moderate",
            "description": f"Significant rainfall detected: {current_precip} mm. Potential for flooding.",
            "issued_at": current.get("time")
        })
    
    # Check upcoming conditions (next 24 hours)
    if hourly:
        max_wind_24h = max(hourly.get("wind_speed_10m", [0])[:24])
        max_precip_24h = max(hourly.get("precipitation", [0])[:24])
        
        if max_wind_24h > 60 and max_wind_24h > current_wind * 1.5:
            alerts.append({
                "type": "Upcoming High Wind Advisory",
                "severity": "moderate",
                "description": f"Strong winds expected in the next 24 hours: up to {max_wind_24h} km/h",
                "issued_at": datetime.now().isoformat()
            })
        
        if max_precip_24h > 20:
            alerts.append({
                "type": "Upcoming Heavy Rain Advisory",
                "severity": "moderate",
                "description": f"Heavy precipitation expected in the next 24 hours: up to {max_precip_24h} mm",
                "issued_at": datetime.now().isoformat()
            })
    
    return {
        "city": city_info["name"],
        "country": city_info["country"],
        "alert_count": len(alerts),
        "alerts": alerts if alerts else [{
            "type": "No Active Alerts",
            "severity": "none",
            "description": "No significant weather hazards detected at this time.",
            "issued_at": datetime.now().isoformat()
        }],
        "note": "Alerts are generated from forecast analysis. For official warnings, consult your local meteorological service."
    }
