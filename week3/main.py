"""
MCP Server that wraps the Open-Meteo API.

Provides two tools: get_coordinates(city_name) and get_weather(latitude, longitude).
Uses STDIO transport. No API key required.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# -----------------------------------------------------------------------------
# Logging: semua output ke stderr agar tidak merusak JSON-RPC di stdout
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
    force=True,
)
logger = logging.getLogger("open-meteo-mcp")

# Constants
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HTTP_TIMEOUT = 10.0  # seconds

mcp = FastMCP(
    "Open-Meteo Weather",
    json_response=True,
)


def _handle_http_error(
    operation: str,
    error: httpx.HTTPError | httpx.TimeoutException | Exception,
) -> str:
    """Return a user-friendly error message for HTTP/network failures."""
    if isinstance(error, httpx.TimeoutException):
        return (
            f"Error [{operation}]: Request timed out after {HTTP_TIMEOUT}s. "
            "The Open-Meteo API may be slow or unreachable. Please try again."
        )
    if isinstance(error, httpx.HTTPStatusError):
        status = error.response.status_code
        return (
            f"Error [{operation}]: HTTP {status}. "
            f"Open-Meteo API returned an error. Please try again later."
        )
    if isinstance(error, httpx.RequestError):
        return (
            f"Error [{operation}]: Network request failed. "
            "Check your internet connection and try again."
        )
    return (
        f"Error [{operation}]: Unexpected error: {type(error).__name__}: {error}. "
        "Please try again."
    )


@mcp.tool()
def get_coordinates(city_name: str) -> str:
    """Get latitude and longitude for a city or location by name.

    Uses the Open-Meteo Geocoding API to search for locations.
    Returns the first matching result with coordinates, or a clear error
    if no results are found.

    Args:
        city_name: The name of the city or location to search for.
            Must be at least 2 characters. Supports fuzzy matching for 3+ chars.

    Returns:
        A formatted string with the location name, country, coordinates,
        and timezone. On failure, returns an error message.

    Example:
        get_coordinates("Berlin") -> "Berlin (Deutschland): lat=52.52, lon=13.41, timezone=Europe/Berlin"
    """
    if not city_name or not city_name.strip():
        return "Error [get_coordinates]: city_name cannot be empty. Please provide a city or location name."

    city_name = city_name.strip()
    if len(city_name) < 2:
        return (
            "Error [get_coordinates]: city_name must be at least 2 characters. "
            "Please provide a longer search term."
        )

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.get(
                GEOCODING_URL,
                params={"name": city_name, "count": 10},
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()

    except httpx.HTTPError as e:
        msg = _handle_http_error("get_coordinates", e)
        logger.exception("get_coordinates failed")
        return msg
    except Exception as e:
        msg = _handle_http_error("get_coordinates", e)
        logger.exception("get_coordinates failed unexpectedly")
        return msg

    results = data.get("results")
    if not results:
        return (
            f"Error [get_coordinates]: No locations found for '{city_name}'. "
            "Try a different spelling or a more general search term."
        )

    locations: list[str] = []
    for r in results[:5]:  # Return up to 5 results
        name = r.get("name", "?")
        country = r.get("country", "?")
        lat = r.get("latitude")
        lon = r.get("longitude")
        tz = r.get("timezone", "?")
        if lat is not None and lon is not None:
            locations.append(f"{name} ({country}): lat={lat:.4f}, lon={lon:.4f}, timezone={tz}")

    if not locations:
        return f"Error [get_coordinates]: No valid coordinates in API response for '{city_name}'."

    return "\n".join(locations)


@mcp.tool()
def get_weather(latitude: float, longitude: float) -> str:
    """Get current weather for a location by latitude and longitude.

    Uses the Open-Meteo Forecast API. Returns current temperature,
    humidity, weather code description, and wind speed.

    Args:
        latitude: Latitude in WGS84 (e.g. 52.52 for Berlin).
            Must be between -90 and 90.
        longitude: Longitude in WGS84 (e.g. 13.41 for Berlin).
            Must be between -180 and 180.

    Returns:
        A formatted string with current weather data. On failure,
        returns an error message.

    Example:
        get_weather(52.52, 13.41) -> "Temperature: 15.2°C, Humidity: 65%, ..."
    """
    if not (-90 <= latitude <= 90):
        return (
            f"Error [get_weather]: latitude must be between -90 and 90, got {latitude}."
        )
    if not (-180 <= longitude <= 180):
        return (
            f"Error [get_weather]: longitude must be between -180 and 180, got {longitude}."
        )

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
    }

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            response = client.get(FORECAST_URL, params=params)
            response.raise_for_status()
            data = response.json()

    except httpx.HTTPError as e:
        msg = _handle_http_error("get_weather", e)
        logger.exception("get_weather failed")
        return msg
    except Exception as e:
        msg = _handle_http_error("get_weather", e)
        logger.exception("get_weather failed unexpectedly")
        return msg

    current = data.get("current")
    if not current:
        return (
            f"Error [get_weather]: No current weather data in API response "
            f"for coordinates ({latitude}, {longitude})."
        )

    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    weather_code = current.get("weather_code")
    wind_speed = current.get("wind_speed_10m")

    def fmt(v: float | int | None) -> str:
        return str(v) if v is not None else "N/A"

    def weather_desc(code: int | None) -> str:
        """Map WMO weather code to human-readable description."""
        if code is None:
            return "N/A"
        codes: dict[int, str] = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
        }
        return codes.get(code, f"Code {code}")

    lines = [
        f"Location: {latitude:.4f}, {longitude:.4f}",
        f"Temperature: {fmt(temp)}°C",
        f"Humidity: {fmt(humidity)}%",
        f"Weather: {weather_desc(weather_code)}",
        f"Wind speed: {fmt(wind_speed)} km/h",
    ]
    return "\n".join(lines)


def main() -> None:
    """Entry point. Runs the MCP server with STDIO transport."""
    mcp.run()


if __name__ == "__main__":
    main()
