"""
Weather MCP Server Package

A Model Context Protocol (MCP) server providing real-time weather data
to LLM clients using the Open-Meteo API.
"""

__version__ = "1.0.0"
__author__ = "Weather MCP Team"

from weather_mcp.server import mcp, main
from weather_mcp.cities import get_city_info, get_supported_cities
from weather_mcp.api import (
    get_current_weather_data,
    get_forecast_data,
    get_weather_alerts_data
)

__all__ = [
    "mcp",
    "main",
    "get_city_info",
    "get_supported_cities",
    "get_current_weather_data",
    "get_forecast_data",
    "get_weather_alerts_data",
]
