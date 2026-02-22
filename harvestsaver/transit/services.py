from decimal import Decimal, ROUND_HALF_UP
from datetime import timedelta
from collections import defaultdict
import hashlib

from django.core.cache import cache

from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import TransportBooking, TransportBookingItem
from farm.models import Hub, Order, Cart, OrderItem
from utils.constants import RATE_PER_KM, TransitOption, BookStatus


@transaction.atomic
def process_order(shipping_address, payment_method, transport, destination_hub_pk,
                  upgrade_non_perishable_express, request):
    from utils.constants import PaymentStatus


    user = request.user
    cart_items = Cart.objects.filter(customer=user)

    destination_hub = get_object_or_404(Hub, pk=destination_hub_pk)
    if not cart_items.exists():
        return None

    total = Cart.total_cart_price(user)
    shipping = round(Decimal("0.09") * total, 2)
    total_cost = total + shipping

    order = Order.objects.filter(
        customer=user,
        status=PaymentStatus.ACTIVE,
        is_checkout_active=True
    ).first()

    if not order:
        order = Order.objects.create(
            customer=user,
            status=PaymentStatus.ACTIVE,
            is_checkout_active=True,
            total_amount=total_cost,
            shipping_address=shipping_address,
            payment_method=payment_method,
        )
    else:
        # Update totals if cart changed
        order.total_amount = total_cost
        order.shipping_address = shipping_address
        order.payment_method = payment_method
        order.save()

        # Clean previous checkout attempt
        order.orderitem_set.all().delete()

    
    order_items = []
    for cart_item in cart_items:

        oi = OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity
        )
        order_items.append(oi)

    hub_map = defaultdict(list)
    for item in order_items:
        hub_map[item.product.hub].append(item)

    today = timezone.now()
    if upgrade_non_perishable_express:
        pass
    
    for hub, items in hub_map.items():
        pickup_date_time = (
            today + timedelta(days=1)
            if any(i.product.is_perishable for i in items)
            else today + timedelta(days=4)
        )

        shipping_cost = calcalate_shipping(items, destination_hub.name)

        booking = TransportBooking.objects.create(
            order=order,
            source_hub=hub,
            destination_hub=destination_hub,
            transport_option=transport,
            cost=shipping_cost,
            requested_pickup_at=pickup_date_time,
            status=BookStatus.PENDING
        )

        for item in items:
            TransportBookingItem.objects.create(
                booking=booking,
                order_item=item
            )
    return order

def make_cache_key(prefix, value):
    """This function makes safe cache keys"""
    safe = value.lower().strip()
    hashed = hashlib.md5(safe.encode()).hexdigest()
    return f"{prefix}:{hashed}"


def calcalate_shipping(cart_items, destination):
    total_shipping = Decimal("0.00")

    hub_groups = defaultdict(list)
    for item in cart_items:
        hub_groups[item.product.hub].append(item)

    for hub, items in hub_groups.items():
        origin_coords = (hub.latitude, hub.longitude)
        desination_coords = get_lat_long(destination)

        distance_km = get_distance(origin_coords, desination_coords)
        distance_km = Decimal(distance_km).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        weight = sum(i.product.unit_weight_kg * i.quantity for i in items)
        hub_cost = distance_km * RATE_PER_KM * weight
        total_shipping += hub_cost

    return total_shipping

def calculate_transport_cost(vehicle_id, distance_km, terrain_type="tarmac"):
    from .models import VehicleCategory, TerrainAdjustment

    vehicle = VehicleCategory.objects.get(id=vehicle_id)
    terrain = TerrainAdjustment.objects.get(zone_type=terrain_type)

    total_price = vehicle.base_fee

    distance_cost = (Decimal(distance_km) * vehicle.rate_per_km) * terrain.multiplier
    total_price += distance_cost

    return round(total_price, 2)

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


def get_distance(origin_coords, destination_coords):
    if not origin_coords or not destination_coords:
        raise ValueError("Both origin and destination coordinates must be provided")
    
    return geodesic(origin_coords, destination_coords).km

def cart_deliery_type(cart_items):
    has_perishable = any(i.product.is_perishable for i in cart_items)
    has_non_perishable = any(not i.product.is_perishable for i in cart_items)

    if has_perishable and has_non_perishable:
        return "mixed"
    elif has_perishable:
        return "perishable"
    return "non_perishable"


