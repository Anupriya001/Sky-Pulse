from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from .models import City

# Create your views here.

class CityListView(ListView):
    """
    A view to list all unique countries.
    """
    model = City
    template_name = 'weather/country_list.html'
    context_object_name = 'countries'

    def get_queryset(self):
        return City.objects.distinct()

class HomeView(TemplateView):
    """
    A simple home page view.
    """
    template_name = 'weather/home.html'
