from decimal import Decimal

from geopy.geocoders import Nominatim

from .models import Location

from farm.models import Hub


def calculate_transport_cost(vehicle_id, distance_km, terrain_type="tarmac"):
    from .models import VehicleCategory, TerrainAdjustment

    vehicle = VehicleCategory.objects.get(id=vehicle_id)
    terrain = TerrainAdjustment.objects.get(zone_type=terrain_type)

    total_price = vehicle.base_fee

    distance_cost = (Decimal(distance_km) * vehicle.rate_per_km) * terrain.multiplier
    total_price += distance_cost

    return round(total_price, 2)

def get_coords_from_name(location_name):
    location_name = location_name.strip().lower()
    
    cached_location = Location.objects.filter(name__iexact=location_name).first()
    if cached_location:
        return cached_location.latitude, cached_location.longitude
    
    geolocator = Nominatim(user_agent="my_agritech_app")
    try:
        location = geolocator.geocode(f"{location_name}, Kenya")
        if location:
            new_loc = Location.objects.create(
                name=location_name,
                latitude=location.latitude,
                longitude=location.longitude,
            )
            return new_loc.latitude, new_loc.longitude
    except Exception as e:
        print(f"Error: {e}")

    return None, None,

def cart_deliery_type(cart_items):
    has_perishable = any(i.product.is_perishable for i in cart_items)
    has_non_perishable = any(not i.product.is_perishable for i in cart_items)

    if has_perishable and has_non_perishable:
        return "mixed"
    elif has_perishable:
        return "perishable"
    return "non_perishable"


