#!/usr/bin/env python3
"""
Example client for Weather MCP Server (HTTP mode).
Demonstrates how to interact with the server programmatically.
"""

import httpx
import asyncio
import json
from typing import Dict, Any


class WeatherMCPClient:
    """Client for Weather MCP Server HTTP API."""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.mcp_endpoint = f"{base_url}/mcp"
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool result
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.mcp_endpoint,
                json={
                    "jsonrpc": "2.0",
                    "method": f"tools/{tool_name}",
                    "params": arguments,
                    "id": 1
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_resource(self, uri: str) -> str:
        """
        Get an MCP resource.
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.mcp_endpoint,
                json={
                    "jsonrpc": "2.0",
                    "method": f"resources/read",
                    "params": {"uri": uri},
                    "id": 1
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for a city."""
        return await self.call_tool("get_current_weather", {"city": city})
    
    async def get_forecast(self, city: str, days: int = 7) -> Dict[str, Any]:
        """Get weather forecast for a city."""
        return await self.call_tool("get_forecast", {"city": city, "days": days})
    
    async def get_alerts(self, city: str) -> Dict[str, Any]:
        """Get weather alerts for a city."""
        return await self.call_tool("get_weather_alerts", {"city": city})
    
    async def get_supported_cities(self) -> str:
        """Get list of supported cities."""
        return await self.get_resource("weather://cities/supported")


async def main():
    """Example usage of the Weather MCP Client."""
    
    print("Weather MCP Server - Example Client\n")
    print("=" * 50)
    
    client = WeatherMCPClient()
    
    try:
        # Example 1: Get current weather
        print("\n1. Getting current weather for London...")
        result = await client.get_current_weather("london")
        print(json.dumps(result, indent=2))
        
        # Example 2: Get 5-day forecast
        print("\n2. Getting 5-day forecast for Paris...")
        result = await client.get_forecast("paris", days=5)
        print(json.dumps(result, indent=2))
        
        # Example 3: Get weather alerts
        print("\n3. Checking weather alerts for Tokyo...")
        result = await client.get_alerts("tokyo")
        print(json.dumps(result, indent=2))
        
        # Example 4: Get supported cities
        print("\n4. Fetching list of supported cities...")
        result = await client.get_supported_cities()
        print(result)
        
        print("\n" + "=" * 50)
        print("✓ All examples completed successfully!")
        
    except httpx.HTTPError as e:
        print(f"\n✗ HTTP Error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
