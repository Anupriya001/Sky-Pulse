from datetime import datetime

from celery import shared_task
from .weather_services import WeatherService
from .models import City, WeatherData

@shared_task
def fetch_and_store_weather_data():
    cities = City.objects.all()
    for city in cities:
        data = WeatherService.get_weather_data(city.latitude, city.longitude, city.name)
        # Example: Save to your WeatherData model (uncomment and adjust fields as needed)
        WeatherData.objects.create(
            city=city,
            temperature=data["temperature"],
            humidity=data["humidity"],
            pressure=data["pressure"],
            wind_speed=data["wind_speed"],
            weather_type=data["weather_type"],
            timestamp=datetime.now(),
        )
        print(f"Fetched weather for {city.name}: {data['temperature']}°C")
