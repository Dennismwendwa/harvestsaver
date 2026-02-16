from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch, Q

from utils.decorators import is_staff
from .forms import TransferRecordForm
from farm.models import Hub, OrderItem
from transit.models import TransportBooking, TransportBookingItem
from logistics.services.dispatch import DispatchService
from utils.constants import BookStatus, ItemStatus
from .models import TransferRecord

@is_staff
def delivery_dashboard(request):
    user = request.user
    my_hub = user.staff_profile.hub

    to_load_w = (
        TransportBooking.objects
        .filter(source_hub=my_hub)
        .filter(~Q(status__in=[BookStatus.IN_TRANSIT, BookStatus.DELIVERED]))
        .filter(
            transportbookingitem__order_item__status__in=[
                ItemStatus.PENDING,
                ItemStatus.PARTIALLY_DISPATCHED
            ]
        )
        .distinct()
        .select_related("order")
        .prefetch_related(
            Prefetch(
                "transportbookingitem_set",
                queryset=TransportBookingItem.objects.select_related(
                    "order_item__product"
                ).filter(
                    order_item__status__in=[
                        ItemStatus.PENDING,
                        ItemStatus.PARTIALLY_DISPATCHED
                    ]
                ),
                to_attr="hub_items"
            )
        )
    )

    incoming = TransferRecord.objects.receivable(my_hub)
    outgoing = TransferRecord.objects.dispatchable(my_hub)
    storage_items = TransferRecord.objects.received_at_hub(my_hub)
    
    if request.method == "POST":
        pass
        return redirect("logistics:delivarly")

    transferForm = TransferRecordForm()

    context={
        "transferForm": transferForm,
        "to_load": to_load_w,
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
        .filter(
            source_hub=my_hub,
            destination_hub=current_item_designation
        )
        .filter(
            transportbookingitem__order_item__status__in=[
                ItemStatus.PENDING,
                ItemStatus.PARTIALLY_DISPATCHED
            ]
        )
        .distinct()
        .select_related("order")
        .prefetch_related(
            Prefetch(
                "transportbookingitem_set",
                queryset=TransportBookingItem.objects
                .select_related("order_item__product")
                .filter(
                    order_item__status__in=[
                        ItemStatus.PENDING,
                        ItemStatus.PARTIALLY_DISPATCHED
                    ]
                ),
                to_attr="hub_items"
            )
        )
        .order_by("created_at")
    )

    if request.method == "POST":
        items_to_load = []

        for route_booking in some_route_items:
            for link in route_booking.hub_items:
                item = link.order_item
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
