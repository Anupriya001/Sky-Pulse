import requests

class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    @staticmethod
    def get_weather_description(code):
        # Basic WMO Code mapping
        if code == 0:
            return "Sunny"
        if 1 <= code <= 3:
            return "Clouds"
        if 45 <= code <= 48:
            return "Fog"
        if 51 <= code <= 67:
            return "Rain"
        if 71 <= code <= 77:
            return "Snow"
        if 80 <= code <= 99:
            return "Storm"
        return "Clear"

    @classmethod
    def get_weather_data(cls, lat, lon, city_name="London"):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "surface_pressure",
                "wind_speed_10m",
                "weather_code",
            ],
            "hourly": "temperature_2m",
            "timezone": "auto",
        }
        response = requests.get(cls.BASE_URL, params=params)
        data = response.json()
        current = data.get("current", {})
        # Compose trend for the last 24 hours (or as needed)
        trend = []
        if "hourly" in data and "time" in data["hourly"] and "temperature_2m" in data["hourly"]:
            trend = [
                {"time": t, "temperature": temp}
                for t, temp in zip(data["hourly"]["time"][:24], data["hourly"]["temperature_2m"][:24])
            ]
        return {
            "city": city_name,
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "pressure": current.get("surface_pressure"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_type": cls.get_weather_description(current.get("weather_code")),
            "timestamp": current.get("time"),
            "trend": trend,
        }