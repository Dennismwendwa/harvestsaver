import requests


def get_driving_distance(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"

    try:
        response = requests.get(url).json()
        if response["code"] == "OK":
            distance_km = response["routes"][0]["distance"] / 1000.0
            return round(distance_km, 2)
    except Exception as e:
        print(f"Routing error: {e}")

    return None

