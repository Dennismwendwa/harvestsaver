import requests
import hashlib

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
    

