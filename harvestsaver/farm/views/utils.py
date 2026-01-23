import requests
import hashlib
from datetime import datetime

from django.conf import settings
from django.core.cache import cache

from geopy.geocoders import Nominatim

def make_cache_key(prefix, value):
    """This function makes safe cache keys"""
    safe = value.lower().strip()
    hashed = hashlib.md5(safe.encode()).hexdigest()
    return f"{prefix}:{hashed}"

def get_lat_long(location_name):
    """
    This function use the city name to get its latitude
    and longitude
    """
    cache_key = make_cache_key("geo", location_name)
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(location_name)

    if location:
        coords = (location.latitude, location.longitude)
        cache.set(cache_key, coords, timeout=60 * 60 * 24 * 30) # 30 days
        return coords
    return None
    
def get_agro_weather(api_key, latitude, longitude):
    """This function sends request to get weather data"""

    base_url = "https://api.agromonitoring.com/agro/1.0/weather/forecast"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None
    

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