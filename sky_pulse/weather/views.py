from .models import WeatherData
# API endpoint to get weather data for a city
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import Nominatim

from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from .models import City
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

class CityListView(ListView):
    """
    A view to list all unique countries.
    """
    model = City

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        if search:
            return City.objects.filter(name__icontains=search).distinct()
        return City.objects.distinct()

class HomeView(TemplateView):
    """
    A simple home page view.
    """
    template_name = 'weather/home.html'
    
    def get_context_data(self, **kwargs):
        """Add watching cities to template context."""
        context = super().get_context_data(**kwargs)
        # show cities marked as watchlisted; fall back to all cities if none
        watching = City.objects.filter(is_watchlisted=True).order_by('name')
        if not watching.exists():
            watching = City.objects.all().order_by('name')
        context['watching_cities'] = watching
        return context


class CitySearchView(View):
    """Class-based view returning JSON list of cities matching `q`."""
    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '').strip()
        if not q:
            return JsonResponse({'results': []})
        qs = City.objects.filter(name__icontains=q, is_watchlisted=False).order_by('name')[:12]
        results = []
        for c in qs:
            results.append({'id': c.id, 'name': c.name, 'country': c.country, 'is_watchlisted': c.is_watchlisted})
        return JsonResponse({'results': results})


@method_decorator(require_POST, name='post')
class ToggleWatchView(View):
    """Class-based view to toggle `is_watchlisted` for a city via POST."""
    def post(self, request, pk, *args, **kwargs):
        try:
            city = get_object_or_404(City, pk=pk)
            city.is_watchlisted = not city.is_watchlisted
            city.save()
            return JsonResponse({'id': city.id, 'is_watchlisted': city.is_watchlisted, 'name': city.name, 'country': city.country})
        except Exception as e:
            return HttpResponseBadRequest(str(e))


class CityCreateView(View):
    """Create a new City via POST. Returns JSON."""
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '').strip()
        country = request.POST.get('country', '').strip()
        watch = request.POST.get('is_watchlisted', '1')
        if not name or not country:
            return HttpResponseBadRequest('Both name and country are required.')
        try:
            geolocator = Nominatim(user_agent="SkyPulse_Weather_App")
            location = geolocator.geocode(f"{name}, {country}")
            if location:
                latitude = location.latitude
                longitude = location.longitude
            else:
                raise ValueError("Could not geocode the provided city and country.")
            city = City.objects.create(name=name, country=country, is_watchlisted=(watch != '0'), latitude=latitude, longitude=longitude)
            return JsonResponse({'id': city.id, 'name': city.name, 'country': city.country, 'is_watchlisted': city.is_watchlisted})
        except Exception as e:
            return HttpResponseBadRequest(str(e))

class CityWeatherDataView(View):
    def get(self, request, pk, *args, **kwargs):
        """
        Return latest weather plus an hourly trend for the past 5 hours (including current hour).
        Trend items use a `time` key in the format `YYYY-MM-DDTHH` so the frontend can match hours.
        Missing hours are filled with 0; current hour will prefer the latest stored value.
        """
        from datetime import timedelta
        from django.utils import timezone

        city = get_object_or_404(City, pk=pk)
        now = timezone.now()

        # Build list of the past 10 hours with 1-hour spacing (oldest -> newest)
        # Produces 10 points: now-9h, now-8h, ..., now-1h, now (oldest -> newest)
        hours = []
        for i in range(9, -1, -1):
            d = (now - timedelta(hours=i)).replace(minute=0, second=0, microsecond=0)
            hours.append(d)

        # Query any stored WeatherData from the earliest hour onwards
        earliest = hours[0]
        stored_qs = WeatherData.objects.filter(city=city, timestamp__gte=earliest).order_by('timestamp')

        # Map stored entries by hour key 'YYYY-MM-DDTHH' -> temperature
        temp_map = {}
        for w in stored_qs:
            key = w.timestamp.strftime('%Y-%m-%dT%H')
            # If there are multiple entries per hour, prefer the latest one
            temp_map[key] = w.temperature

        # Latest weather entry (any time) to use as fallback for current hour
        latest = WeatherData.objects.filter(city=city).order_by('-timestamp').first()
        if not latest:
            return JsonResponse({'error': 'No weather data found.'}, status=404)

        latest_key = latest.timestamp.strftime('%Y-%m-%dT%H')

        # Build trend for each hour key (use stored value, else 0; prefer latest for current hour)
        trend = []
        for d in hours:
            key = d.strftime('%Y-%m-%dT%H')
            if key in temp_map:
                temp = temp_map[key]
            elif key == latest_key and latest.temperature is not None:
                temp = latest.temperature
            else:
                temp = 0
            trend.append({'time': key, 'temperature': temp})

        data = {
            'city': city.name,
            'country': city.country,
            'temperature': latest.temperature,
            'humidity': latest.humidity,
            'pressure': latest.pressure,
            'wind_speed': latest.wind_speed,
            'timestamp': latest.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'trend': trend,
        }

        return JsonResponse(data)