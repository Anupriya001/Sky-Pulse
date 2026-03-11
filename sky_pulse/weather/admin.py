from django.contrib import admin

# Register your models here.

from .models import City, WeatherData
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_watchlisted', 'last_updated')
    list_filter = ('country', 'is_watchlisted')
    search_fields = ('name', 'country')

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('city', 'temperature', 'humidity', 'wind_speed', 'timestamp')
    list_filter = ('city', 'timestamp')
    search_fields = ('city__name',)