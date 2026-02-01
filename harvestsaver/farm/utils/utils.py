from django.utils import timezone
from datetime import datetime
from math import sqrt

from django.conf import settings
from django.core.cache import cache

from farm.models import Hub
from .helpers import make_cache_key, get_lat_long, get_agro_weather


def weather_data(city, country):
    """Request for weather data"""
    raw_key = f"{city}-{country}"
    cache_key = make_cache_key("weather", raw_key)
    cached = cache.get(cache_key)
    if cached:
        return cached

    area_coodinates = get_lat_long(f"{city}, {country}")

    api_key = settings.WEATHER_API_KEY
    if area_coodinates:
        latitude, longitude = area_coodinates
    else:
        latitude, longitude = 51.51, -0.13

    agro_weather_data = get_agro_weather(api_key, latitude, longitude) or []

    weather_ui_data = []
    for item in agro_weather_data[:8]:  # next 24 hours only
        temp_k = item["main"]["temp"]
        weather_ui_data.append({
            "dt_readable": datetime.fromtimestamp(item["dt"]),
            "temp_c": round(temp_k - 273.15, 1),
            "humidity": item["main"]["humidity"],
            "condition": item["weather"][0]["main"],
            "icon": item["weather"][0]["icon"],
        })

    cache.set(cache_key, weather_ui_data, timeout=60 * 15) # 15 min
    return weather_ui_data


def assign_hub_to_farm(farm):
    hubs = Hub.objects.filter(is_active=True)

    farm_lat = float(farm.latitude)
    farm_lng = float(farm.longitude)

    def distance(h):
        return sqrt(
            (float(h.latitude) - farm_lat) ** 2 +
            (float(h.longitude) - farm_lng) ** 2
        )
    
    nearest = min(hubs, key=distance)
    farm.hub = nearest
    farm.save()


def get_default_range():
    """
    Returns time range of current month
    """
    now = timezone.now()
    return now.replace(day=1, hour=0, minute=0, second=0)

