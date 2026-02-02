import requests

    
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
    

