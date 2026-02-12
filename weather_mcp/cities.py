"""
Supported cities database with coordinates for weather lookups.
"""

SUPPORTED_CITIES = {
    # North America
    "new_york": {
        "lat": 40.7128,
        "lon": -74.0060,
        "name": "New York",
        "country": "USA",
        "timezone": "America/New_York"
    },
    "los_angeles": {
        "lat": 34.0522,
        "lon": -118.2437,
        "name": "Los Angeles",
        "country": "USA",
        "timezone": "America/Los_Angeles"
    },
    "chicago": {
        "lat": 41.8781,
        "lon": -87.6298,
        "name": "Chicago",
        "country": "USA",
        "timezone": "America/Chicago"
    },
    "san_francisco": {
        "lat": 37.7749,
        "lon": -122.4194,
        "name": "San Francisco",
        "country": "USA",
        "timezone": "America/Los_Angeles"
    },
    "toronto": {
        "lat": 43.6532,
        "lon": -79.3832,
        "name": "Toronto",
        "country": "Canada",
        "timezone": "America/Toronto"
    },
    "vancouver": {
        "lat": 49.2827,
        "lon": -123.1207,
        "name": "Vancouver",
        "country": "Canada",
        "timezone": "America/Vancouver"
    },
    "mexico_city": {
        "lat": 19.4326,
        "lon": -99.1332,
        "name": "Mexico City",
        "country": "Mexico",
        "timezone": "America/Mexico_City"
    },
    
    # Europe
    "london": {
        "lat": 51.5074,
        "lon": -0.1278,
        "name": "London",
        "country": "UK",
        "timezone": "Europe/London"
    },
    "paris": {
        "lat": 48.8566,
        "lon": 2.3522,
        "name": "Paris",
        "country": "France",
        "timezone": "Europe/Paris"
    },
    "berlin": {
        "lat": 52.5200,
        "lon": 13.4050,
        "name": "Berlin",
        "country": "Germany",
        "timezone": "Europe/Berlin"
    },
    "madrid": {
        "lat": 40.4168,
        "lon": -3.7038,
        "name": "Madrid",
        "country": "Spain",
        "timezone": "Europe/Madrid"
    },
    "rome": {
        "lat": 41.9028,
        "lon": 12.4964,
        "name": "Rome",
        "country": "Italy",
        "timezone": "Europe/Rome"
    },
    "amsterdam": {
        "lat": 52.3676,
        "lon": 4.9041,
        "name": "Amsterdam",
        "country": "Netherlands",
        "timezone": "Europe/Amsterdam"
    },
    
    # Asia
    "tokyo": {
        "lat": 35.6762,
        "lon": 139.6503,
        "name": "Tokyo",
        "country": "Japan",
        "timezone": "Asia/Tokyo"
    },
    "beijing": {
        "lat": 39.9042,
        "lon": 116.4074,
        "name": "Beijing",
        "country": "China",
        "timezone": "Asia/Shanghai"
    },
    "shanghai": {
        "lat": 31.2304,
        "lon": 121.4737,
        "name": "Shanghai",
        "country": "China",
        "timezone": "Asia/Shanghai"
    },
    "singapore": {
        "lat": 1.3521,
        "lon": 103.8198,
        "name": "Singapore",
        "country": "Singapore",
        "timezone": "Asia/Singapore"
    },
    "seoul": {
        "lat": 37.5665,
        "lon": 126.9780,
        "name": "Seoul",
        "country": "South Korea",
        "timezone": "Asia/Seoul"
    },
    "mumbai": {
        "lat": 19.0760,
        "lon": 72.8777,
        "name": "Mumbai",
        "country": "India",
        "timezone": "Asia/Kolkata"
    },
    "dubai": {
        "lat": 25.2048,
        "lon": 55.2708,
        "name": "Dubai",
        "country": "UAE",
        "timezone": "Asia/Dubai"
    },
    
    # Oceania
    "sydney": {
        "lat": -33.8688,
        "lon": 151.2093,
        "name": "Sydney",
        "country": "Australia",
        "timezone": "Australia/Sydney"
    },
    "melbourne": {
        "lat": -37.8136,
        "lon": 144.9631,
        "name": "Melbourne",
        "country": "Australia",
        "timezone": "Australia/Melbourne"
    },
    "auckland": {
        "lat": -36.8485,
        "lon": 174.7633,
        "name": "Auckland",
        "country": "New Zealand",
        "timezone": "Pacific/Auckland"
    },
    
    # South America
    "sao_paulo": {
        "lat": -23.5505,
        "lon": -46.6333,
        "name": "São Paulo",
        "country": "Brazil",
        "timezone": "America/Sao_Paulo"
    },
    "buenos_aires": {
        "lat": -34.6037,
        "lon": -58.3816,
        "name": "Buenos Aires",
        "country": "Argentina",
        "timezone": "America/Argentina/Buenos_Aires"
    },
    "rio_de_janeiro": {
        "lat": -22.9068,
        "lon": -43.1729,
        "name": "Rio de Janeiro",
        "country": "Brazil",
        "timezone": "America/Sao_Paulo"
    },
    
    # Africa
    "cairo": {
        "lat": 30.0444,
        "lon": 31.2357,
        "name": "Cairo",
        "country": "Egypt",
        "timezone": "Africa/Cairo"
    },
    "cape_town": {
        "lat": -33.9249,
        "lon": 18.4241,
        "name": "Cape Town",
        "country": "South Africa",
        "timezone": "Africa/Johannesburg"
    },
}


def get_city_info(city: str) -> dict:
    """Get city information by name (case-insensitive)."""
    city_key = city.lower().replace(" ", "_")
    if city_key not in SUPPORTED_CITIES:
        raise ValueError(
            f"City '{city}' not supported. Use get_supported_cities() to see available cities."
        )
    return SUPPORTED_CITIES[city_key]


def get_supported_cities() -> list[dict]:
    """Get list of all supported cities with their information."""
    return [
        {
            "key": key,
            "name": info["name"],
            "country": info["country"],
            "coordinates": f"{info['lat']}, {info['lon']}"
        }
        for key, info in SUPPORTED_CITIES.items()
    ]
