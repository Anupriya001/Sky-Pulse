from django.db import models

# Create your models here.
class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    is_watchlisted = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'cities'

    def __str__(self):
        return f"{self.name}, {self.country}"

class WeatherData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    weather_type = models.CharField(
        max_length=20,
        choices=[
            ('Clear', 'Clear'),
            ('Clouds', 'Clouds'),
            ('Rain', 'Rain'),
            ('Snow', 'Snow'),
            ('Drizzle', 'Drizzle'),
            ('Thunderstorm', 'Thunderstorm'),
            ('Mist', 'Mist'),
            ('Smoke', 'Smoke'),
            ('Haze', 'Haze'),
            ('Dust', 'Dust'),
            ('Fog', 'Fog'),
            ('Sand', 'Sand'),
            ('Ash', 'Ash'),
            ('Squall', 'Squall'),
            ('Tornado', 'Tornado')
        ],
        default='Clear'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"WeatherData for {self.city.name} at {self.timestamp}"
