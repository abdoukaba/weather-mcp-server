"""
Weather MCP Server - Provides real-time weather data to LLM clients.

This server implements the Model Context Protocol (MCP) to provide weather
information including current conditions, forecasts, and alerts.
"""

import sys
import json
import logging
from typing import Any
from fastmcp import FastMCP
from weather_mcp.api import (
    get_current_weather_data,
    get_forecast_data,
    get_weather_alerts_data
)
from weather_mcp.cities import get_supported_cities


# Configure logging based on transport
def setup_logging(transport: str = "stdio"):
    """Configure appropriate logging for the transport type."""
    if transport == "stdio":
        # For STDIO, log to stderr to avoid interfering with protocol
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stderr
        )
    else:
        # For HTTP, use JSON logging
        logging.basicConfig(
            level=logging.INFO,
            format='{"timestamp":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}',
            handlers=[logging.StreamHandler(sys.stdout)]
        )


# Initialize MCP server
mcp = FastMCP("weather-server")

logger = logging.getLogger("weather-mcp")


# Tools (Functions that LLMs can call)

@mcp.tool()
async def get_current_weather(city: str) -> dict[str, Any]:
    """
    Get current weather conditions for a city.
    
    Returns temperature, conditions, humidity, wind speed, and more.
    Use city names like 'london', 'new_york', 'tokyo', etc.
    
    Args:
        city: Name of the city (case-insensitive, use underscores for spaces)
        
    Example:
        get_current_weather("paris")
        get_current_weather("new_york")
    """
    logger.info(f"Getting current weather for {city}")
    try:
        result = await get_current_weather_data(city)
        logger.info(f"Successfully retrieved weather for {city}")
        return result
    except ValueError as e:
        logger.error(f"City not found: {city}")
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error getting weather for {city}: {e}")
        raise Exception(f"Failed to retrieve weather data: {str(e)}")


@mcp.tool()
async def get_forecast(city: str, days: int = 7) -> dict[str, Any]:
    """
    Get weather forecast for a city for the specified number of days.
    
    Returns daily forecasts including temperature ranges, precipitation,
    wind conditions, and sunrise/sunset times.
    
    Args:
        city: Name of the city (case-insensitive, use underscores for spaces)
        days: Number of days to forecast (1-16, default is 7)
        
    Example:
        get_forecast("london", days=5)
        get_forecast("tokyo")
    """
    logger.info(f"Getting {days}-day forecast for {city}")
    try:
        if not 1 <= days <= 16:
            raise ValueError("Days must be between 1 and 16")
        result = await get_forecast_data(city, days)
        logger.info(f"Successfully retrieved forecast for {city}")
        return result
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error getting forecast for {city}: {e}")
        raise Exception(f"Failed to retrieve forecast data: {str(e)}")


@mcp.tool()
async def get_weather_alerts(city: str) -> dict[str, Any]:
    """
    Get weather alerts and warnings for a city.
    
    Analyzes current and upcoming conditions to identify potential
    weather hazards such as high winds, extreme temperatures, or
    heavy precipitation.
    
    Note: These are generated alerts based on forecast analysis,
    not official meteorological warnings.
    
    Args:
        city: Name of the city (case-insensitive, use underscores for spaces)
        
    Example:
        get_weather_alerts("miami")
        get_weather_alerts("singapore")
    """
    logger.info(f"Getting weather alerts for {city}")
    try:
        result = await get_weather_alerts_data(city)
        logger.info(f"Successfully retrieved alerts for {city}")
        return result
    except ValueError as e:
        logger.error(f"City not found: {city}")
        raise ValueError(str(e))
    except Exception as e:
        logger.error(f"Error getting alerts for {city}: {e}")
        raise Exception(f"Failed to retrieve alert data: {str(e)}")


# Resources (Static or dynamic data that LLMs can read)

@mcp.resource("weather://cities/supported")
def get_supported_cities_resource() -> str:
    """
    Resource providing list of all supported cities.
    
    Returns JSON list of cities with their coordinates and country.
    """
    logger.info("Fetching supported cities list")
    cities = get_supported_cities()
    return json.dumps({
        "description": "List of all cities supported by the weather server",
        "total_cities": len(cities),
        "cities": cities
    }, indent=2)


@mcp.resource("weather://api/info")
def get_api_info() -> str:
    """
    Resource providing information about the weather API.
    
    Returns details about the Open-Meteo API and its capabilities.
    """
    return json.dumps({
        "api_name": "Open-Meteo",
        "api_url": "https://open-meteo.com",
        "description": "Free weather API with no authentication required",
        "features": [
            "Current weather conditions",
            "Weather forecasts up to 16 days",
            "Historical weather data",
            "No API key required",
            "High-resolution weather models"
        ],
        "data_sources": [
            "NOAA GFS & HRRR",
            "DWD ICON",
            "Météo-France ARPEGE & AROME"
        ],
        "update_frequency": "Hourly",
        "coverage": "Global"
    }, indent=2)


# Health check endpoint for container orchestration
@mcp.resource("health://status")
def health_check() -> str:
    """
    Health check endpoint for monitoring and orchestration.
    
    Returns server status and basic diagnostics.
    """
    return json.dumps({
        "status": "healthy",
        "service": "weather-mcp-server",
        "version": "1.0.0",
        "timestamp": "2025-01-19T18:00:00Z"
    })


def main():
    """
    Main entry point for the MCP server.
    
    Can be run in two modes:
    1. STDIO transport for local development (default)
    2. HTTP transport for production deployment
    
    Set via command line arguments or environment variables.
    """
    import os
    
    # Determine transport mode
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    # Check command line args
    if len(sys.argv) > 1:
        if sys.argv[1] == "--http":
            transport = "http"
        elif sys.argv[1] == "--stdio":
            transport = "stdio"
    
    # Setup logging
    setup_logging(transport)
    logger.info(f"Starting Weather MCP Server in {transport} mode")
    
    # Run server with appropriate transport
    if transport == "http":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "3000"))
        path = os.getenv("MCP_PATH", "/mcp")
        
        logger.info(f"Starting HTTP server on {host}:{port}{path}")
        mcp.run(
            transport="http",
            host=host,
            port=port,
            path=path
        )
    else:
        logger.info("Starting STDIO server")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
