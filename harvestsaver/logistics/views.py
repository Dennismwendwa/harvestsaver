from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Prefetch

from .forms import TransferRecordForm
from farm.models import Hub, OrderItem
from transit.models import TransportBooking
from logistics.services.dispatch import DispatchService



def delivery_dashboard(request):
    user = request.user
    my_hub = user.staff_profile.hub

    to_load = (
        TransportBooking.objects
        .filter(source_hub=my_hub)
        .select_related("order")
        .prefetch_related(
            Prefetch(
                "order__items",
                queryset=OrderItem.objects.filter(
                    product__hub=my_hub
                ),
                to_attr="hub_items"
            )
        )
    ).order_by("created_at")
    
    if request.method == "POST":
        pass

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
                    product__hub=my_hub
                ),
                to_attr="hub_items"
            )
        )
    ).order_by("created_at")

    if request.method == "POST":
        selected_items = request.POST.getlist("items")
        items = OrderItem.objects.filter(
            id__in=selected_items,
            product__hub=my_hub
        )

        DispatchService.prepare_dispatch(
            user=user,
            booking=booking,
            items=items
        )


    context = {
        "booking": booking,
        "some_route_items": some_route_items,
    }
    return render(request, "logistics/delivery/booking_dispach.html", context)

