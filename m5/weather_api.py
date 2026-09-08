import requests


def get_weather(latitude, longitude):
    """
    Fetch current weather data for a given GPS location
    using the Open-Meteo API.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,precipitation,rain",
        "hourly": "precipitation_probability",
        "forecast_days": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})

        # Get precipitation probability for the current hour
        precipitation_probability = None

        if hourly.get("precipitation_probability"):
            precipitation_probability = hourly["precipitation_probability"][0]

        weather_data = {
            "latitude": latitude,
            "longitude": longitude,
            "temperature": current.get("temperature_2m"),
            "precipitation": current.get("precipitation"),
            "rain": current.get("rain"),
            "precipitation_probability": precipitation_probability
        }

        return weather_data

    except requests.RequestException as e:
        print("Weather API error:", e)
        return None


# Test the function directly
if __name__ == "__main__":

    latitude = 28.6
    longitude = 77.2

    weather = get_weather(latitude, longitude)

    if weather:
        print("\nWeather data received:")
        print(weather)
    else:
        print("\nFailed to get weather data.")