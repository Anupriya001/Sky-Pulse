from celery.schedules import crontab
from celery import Celery

app = Celery('sky_pulse')

app.conf.beat_schedule = {
    'fetch-weather-every-30-minutes': {
        'task': 'weather.tasks.fetch_and_store_weather_data',
        'schedule': crontab(minute='*/30'),  # every 30 minutes
    },
}

# ...existing code...