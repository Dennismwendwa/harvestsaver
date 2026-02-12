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
                ),
                to_attr="hub_items"
            )
        )
    ).order_by("created_at")

    incoming = TransferRecord.objects.receivable(my_hub)
    outgoing = TransferRecord.objects.dispatchable(my_hub)
    storage_items = TransferRecord.objects.received_at_hub(my_hub)
    
    if request.method == "POST":
        pass
        return redirect("logistics:delivarly")

    transferForm = TransferRecordForm()

    context={
        "transferForm": transferForm,
        "to_load": to_load,
        "incoming": incoming,
        "outgoing": outgoing,
        "storage_items": storage_items,
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
                    #status=ItemStatus.PENDING,
                ),
                to_attr="hub_items"
            )
        )
    ).order_by("created_at")

    if request.method == "POST":
        items_to_load = []

        for route_booking in some_route_items:
            for item in route_booking.order.hub_items:
                qty = int(request.POST.get(f"qty_{item.id}", 0))

                if qty > 0:
                    items_to_load.append((item, qty))
        try:
            DispatchService.prepare_dispatch(
                user=user,
                booking=booking,
                items=items_to_load
            )
            messages.success(request, "Items Dispatched successfully")
        except Exception as e:
            messages.error(request, f"{e}")
        return redirect("logistics:delivarly")

    context = {
        "booking": booking,
        "some_route_items": some_route_items,
    }
    return render(request, "logistics/delivery/booking_dispach.html", context)

