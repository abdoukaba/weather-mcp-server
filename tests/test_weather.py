"""
Test suite for Weather MCP Server

Run with: pytest tests/test_weather.py -v
"""

import pytest
import asyncio
from weather_mcp.api import (
    get_current_weather_data,
    get_forecast_data,
    get_weather_alerts_data
)
from weather_mcp.cities import get_city_info, get_supported_cities


class TestCities:
    """Test city database functionality."""
    
    def test_get_city_info_valid(self):
        """Test retrieving valid city information."""
        city = get_city_info("london")
        assert city["name"] == "London"
        assert city["country"] == "UK"
        assert "lat" in city
        assert "lon" in city
    
    def test_get_city_info_case_insensitive(self):
        """Test that city lookup is case-insensitive."""
        city1 = get_city_info("PARIS")
        city2 = get_city_info("paris")
        assert city1 == city2
    
    def test_get_city_info_invalid(self):
        """Test that invalid city raises ValueError."""
        with pytest.raises(ValueError):
            get_city_info("nonexistent_city")
    
    def test_get_supported_cities(self):
        """Test getting list of all supported cities."""
        cities = get_supported_cities()
        assert len(cities) > 0
        assert isinstance(cities, list)
        assert all("name" in city for city in cities)
        assert all("country" in city for city in cities)


class TestWeatherAPI:
    """Test weather API functionality."""
    
    @pytest.mark.asyncio
    async def test_get_current_weather(self):
        """Test getting current weather data."""
        weather = await get_current_weather_data("london")
        
        # Check structure
        assert "city" in weather
        assert "temperature" in weather
        assert "conditions" in weather
        assert "humidity" in weather
        assert "wind" in weather
        
        # Check temperature data
        assert "value" in weather["temperature"]
        assert "unit" in weather["temperature"]
        assert weather["temperature"]["unit"] == "°C"
        
        # Check wind data
        assert "speed" in weather["wind"]
        assert "direction" in weather["wind"]
    
    @pytest.mark.asyncio
    async def test_get_forecast_default(self):
        """Test getting default 7-day forecast."""
        forecast = await get_forecast_data("paris")
        
        assert "city" in forecast
        assert "forecast" in forecast
        assert len(forecast["forecast"]) == 7
        
        # Check first day structure
        day = forecast["forecast"][0]
        assert "date" in day
        assert "temperature" in day
        assert "conditions" in day
        assert "precipitation" in day
    
    @pytest.mark.asyncio
    async def test_get_forecast_custom_days(self):
        """Test getting custom number of forecast days."""
        forecast = await get_forecast_data("tokyo", days=3)
        assert len(forecast["forecast"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_forecast_invalid_days(self):
        """Test that invalid days parameter raises ValueError."""
        with pytest.raises(ValueError):
            await get_forecast_data("tokyo", days=0)
        
        with pytest.raises(ValueError):
            await get_forecast_data("tokyo", days=17)
    
    @pytest.mark.asyncio
    async def test_get_weather_alerts(self):
        """Test getting weather alerts."""
        alerts = await get_weather_alerts_data("new_york")
        
        assert "city" in alerts
        assert "alert_count" in alerts
        assert "alerts" in alerts
        assert isinstance(alerts["alerts"], list)
        
        # Check alert structure
        if alerts["alert_count"] > 0:
            alert = alerts["alerts"][0]
            assert "type" in alert
            assert "severity" in alert
            assert "description" in alert
    
    @pytest.mark.asyncio
    async def test_invalid_city_raises_error(self):
        """Test that invalid city raises appropriate error."""
        with pytest.raises(ValueError):
            await get_current_weather_data("invalid_city_name")


class TestMCPServer:
    """Test MCP server functionality."""
    
    def test_server_import(self):
        """Test that server can be imported."""
        from weather_mcp.server import mcp, main
        assert mcp is not None
        assert callable(main)
    
    def test_tools_registered(self):
        """Test that all tools are registered."""
        from weather_mcp.server import mcp
        
        # FastMCP exposes tools via _tools attribute
        tool_names = [tool.name for tool in mcp._tools]
        
        assert "get_current_weather" in tool_names
        assert "get_forecast" in tool_names
        assert "get_weather_alerts" in tool_names
    
    def test_resources_registered(self):
        """Test that all resources are registered."""
        from weather_mcp.server import mcp
        
        # FastMCP exposes resources via _resources attribute
        resource_uris = [res.uri for res in mcp._resources]
        
        assert "weather://cities/supported" in resource_uris
        assert "weather://api/info" in resource_uris


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
