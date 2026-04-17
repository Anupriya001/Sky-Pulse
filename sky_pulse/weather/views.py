from .models import WeatherData
# API endpoint to get weather data for a city
from django.views.decorators.csrf import csrf_exempt

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
            city = City.objects.create(name=name, country=country, is_watchlisted=(watch != '0'))
            return JsonResponse({'id': city.id, 'name': city.name, 'country': city.country, 'is_watchlisted': city.is_watchlisted})
        except Exception as e:
            return HttpResponseBadRequest(str(e))

class CityWeatherDataView(View):
    def get(self, request, pk, *args, **kwargs):
        from datetime import timedelta
        from django.utils import timezone
        city = get_object_or_404(City, pk=pk)
        now = timezone.now()
        ten_days_ago = now - timedelta(days=10)
        # Get weather data for the last 10 days, ordered by timestamp ascending
        trend_qs = WeatherData.objects.filter(city=city, timestamp__gte=ten_days_ago).order_by('timestamp')
        trend = [
            {'date': w.timestamp.strftime('%Y-%m-%d'), 'temperature': w.temperature}
            for w in trend_qs
        ]
        # Get the latest weather data for the city
        weather = trend_qs.last() or WeatherData.objects.filter(city=city).order_by('-timestamp').first()
        if not weather:
            return JsonResponse({'error': 'No weather data found.'}, status=404)
        data = {
            'city': city.name,
            'country': city.country,
            'temperature': weather.temperature,
            'humidity': weather.humidity,
            'pressure': weather.pressure,
            'wind_speed': weather.wind_speed,
            'timestamp': weather.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'trend': trend
        }
        return JsonResponse(data)