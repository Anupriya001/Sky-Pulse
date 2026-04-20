from django.db import migrations

def populate_lat_lon(apps, schema_editor):
    City = apps.get_model('weather', 'City')
    # Example static mapping; extend as needed
    city_coords = {
        'London': (51.5074, -0.1278),
        'Delhi': (28.6139, 77.2090),
        'Kolkata': (22.5726, 88.3639),
        'Mumbai': (19.0760, 72.8777),
        'Singapore': (1.3521, 103.8198),
        'Kochi': (9.9312, 76.2673),
        # Add more cities as needed
    }
    for city in City.objects.all():
        coords = city_coords.get(city.name)
        if coords:
            city.latitude, city.longitude = coords
            city.save(update_fields=["latitude", "longitude"])

class Migration(migrations.Migration):
    dependencies = [
        ('weather', '0003_city_latitude_city_longitude'),
    ]
    operations = [
        migrations.RunPython(populate_lat_lon, reverse_code=migrations.RunPython.noop),
    ]
