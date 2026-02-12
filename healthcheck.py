#!/usr/bin/env python3
"""
Health check script for Weather MCP Server.
Can be used by container orchestration systems or monitoring tools.
"""

import httpx
import sys
import json
from typing import Dict, Any


def check_health(url: str = "http://localhost:3000/health", timeout: int = 5) -> Dict[str, Any]:
    """
    Check server health endpoint.
    
    Args:
        url: Health check endpoint URL
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with health status
    """
    try:
        response = httpx.get(url, timeout=timeout)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "healthy": True,
            "status_code": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "data": data
        }
    except httpx.TimeoutException:
        return {
            "healthy": False,
            "error": "Health check timeout",
            "status_code": None
        }
    except httpx.HTTPStatusError as e:
        return {
            "healthy": False,
            "error": f"HTTP error: {e.response.status_code}",
            "status_code": e.response.status_code
        }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "status_code": None
        }


def main():
    """Main entry point for health check script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check Weather MCP Server health")
    parser.add_argument(
        "--url",
        default="http://localhost:3000/health",
        help="Health check endpoint URL"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Request timeout in seconds"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    args = parser.parse_args()
    
    result = check_health(args.url, args.timeout)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["healthy"]:
            print(f"✓ Server is healthy")
            print(f"  Status: {result.get('status_code', 'N/A')}")
            print(f"  Response time: {result.get('response_time_ms', 0):.2f}ms")
        else:
            print(f"✗ Server is unhealthy")
            print(f"  Error: {result.get('error', 'Unknown')}")
    
    sys.exit(0 if result["healthy"] else 1)


if __name__ == "__main__":
    main()
