from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Q

from .forms import TransferRecordForm
from farm.models import Hub, OrderItem
from transit.models import TransportBooking
from logistics.services.dispatch import DispatchService
from utils.constants import BookStatus, ItemStatus
from .models import TransferRecord


def delivery_dashboard(request):
    user = request.user
    my_hub = user.staff_profile.hub

    to_load = (
        TransportBooking.objects
        .filter(source_hub=my_hub)
        .filter(
            ~Q(status=BookStatus.IN_TRANSIT) &
            ~Q(status=BookStatus.DELIVERED)
        )
        .distinct()
        .select_related("order")
        .prefetch_related(
            Prefetch(
                "order__items",
                queryset=OrderItem.objects.filter(
                    product__hub=my_hub,
                    #status__in=[ItemStatus.PENDING, ItemStatus.PARTIALLY_DISPATCHED],
                ),
                to_attr="hub_items"
            )
        )
    ).order_by("created_at")

    items_in_transit = TransferRecord.objects.in_transit_to(my_hub)

    print()
    print(items_in_transit)
    print()
    print()
    
    if request.method == "POST":
        pass
        return redirect("logistics:delivarly")

    transferForm = TransferRecordForm()

    context={
        "transferForm": transferForm,
        "to_load": to_load,
    }
    return render(request, "logistics/delivery/delivery_dashboard.html", context)

def booking_dispach(request, booking_id):
    user = request.user
    my_hub = user.staff_profile.hub
    booking = get_object_or_404(TransportBooking, pk=booking_id)

    current_item_designation = booking.destination_hub
    some_route_items = (
        TransportBooking.objects
        .filter(source_hub=my_hub, destination_hub=current_item_designation)
        .select_related("order")
        .prefetch_related(
            Prefetch(
                "order__items",
                queryset=OrderItem.objects.filter(
                    product__hub=my_hub,
                    status=ItemStatus.PENDING,
                ),
                to_attr="hub_items"
            )
        )
    ).order_by("created_at")

    print()
    for b in some_route_items:
        print()
        print(f"book: {b.id} - {b.status}")
        print(f"order: {b.order.order_reference}")
        items = OrderItem.objects.filter(order=b.order)
        for i in items:
            print(f"id: {i.id} - {i.status}")

    if request.method == "POST":
        items_to_load = []

        for route_booking in some_route_items:
            for item in route_booking.order.hub_items:
                qty = int(request.POST.get(f"qty_{item.id}", 0))

                if qty > 0:
                    items_to_load.append((item, qty))

        DispatchService.prepare_dispatch(
            user=user,
            booking=booking,
            items=items_to_load
        )
        return redirect("logistics:delivarly")


    context = {
        "booking": booking,
        "some_route_items": some_route_items,
    }
    return render(request, "logistics/delivery/booking_dispach.html", context)

