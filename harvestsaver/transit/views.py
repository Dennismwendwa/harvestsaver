from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from .services import calculate_transport_cost, get_coords_from_name, cart_deliery_type
from .utils import get_driving_distance

from .models import TransportBooking, Quote
from .forms import QuoteForm


def transportoptions(request):
    
    context = {}
    return render(request, "transit/transportoptions.html", context)


def transporthome(request):
    """This view is for transport quote"""
    if request.method == "POST":
        form = QuoteForm(request.POST)
        if form.is_valid():
            departure = form.cleaned_data["departure"]
            delivery = form.cleaned_data["delivery"]
            weight = form.cleaned_data["weight"]
            dimensions = form.cleaned_data["dimensions"]
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            message = form.cleaned_data["message"]

            Quote.objects.create(
                departure=departure,
                delivery=delivery,
                weight=weight,
                dimensions=dimensions,
                name=name,
                email=email,
                phone=phone,
                message=message,
            )
            messages.success(request, (
                                       f"Your quote request has been sent "
                                       f"successfully. Thank you!")
                                       )

            return redirect("transit:transportquote")
        else:
            print(form.errors)
            error_list = []
            for error in form.errors:
                error_list.append(error)
            error_message = ", ".join(error_list)
            messages.warning(request, f"{error_message}")
            return redirect("transit:transportquote")
    
            #return render(request, "transit/transport.html", {"form": form})
    
    return render(request, "transit/transport.html", {})


@permission_required("transit.change_transport_booking", raise_exception=True)
def all_transport(request):

    transports = TransportBooking.objects.filter(status="Pending")

    delivered = TransportBooking.objects.filter(status="Delivered")

    context = {
        "transports": transports,
        "delivered": delivered,
    }
    return render(request, "transit/all_transport.html", context)


def delivered(request, pk):
    transport = get_object_or_404(TransportBooking, pk=pk)
    transport.status = "Delivered"
    transport.delivery_dateTime = timezone.now()
    transport.save()

    messages.success(request, (
                              f"Order {transport.order.transaction_id} "
                              f"updated successfully")
                              )
    return redirect("transit:transporthome")

def get_quote(request):
    if request.method == "GET":
        vehicle_id = request.GET.get("vehicle_id")
        dist = request.GET.get("distnace")
        terrain = request.GET.get("terrain", "tarmac")

        price = calculate_transport_cost(vehicle_id, dist, 0, terrain)

        return JsonResponse({"estimated_cost": price})
    

def calculate_trip(request):
    origin_name = request.GET.get("from")
    dest_name = request.GET.get("to")
    vehicle_id = request.GET.get("vehicle_id")
    dist = request.GET.get("distnace")
    terrain = request.GET.get("terrain", "tarmac")

    lat1, lon1 = get_coords_from_name(origin_name)
    lat2, lon2 = get_coords_from_name(dest_name)

    if lat1 and lat2:
        distance_km = get_driving_distance(lat1, lon1, lat2, lon2)
        totol_cost = calculate_transport_cost(vehicle_id, distance_km, 0, terrain)
        return JsonResponse({"distance_km": distance_km,
                             "total_cost": totol_cost,
                             "status": "success"})
    return JsonResponse({"error": "Location not found"}, status=404)

