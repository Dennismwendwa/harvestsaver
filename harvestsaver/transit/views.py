from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

from .models import TransportBooking, Quote
from .forms import QuoteForm


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
            return redirect("transit:transporthome")
        else:
            print(form.errors)
            error_list = []
            for error in form.errors:
                error_list.append(error)
            error_message = ", ".join(error_list)
            messages.error(request, f"{error_message}")
            return redirect("transit:transporthome")
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














