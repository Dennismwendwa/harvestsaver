from django.shortcuts import render, redirect
from django.contrib import messages

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
            form = form
            return render(request, "transit/transport.html", {"form": form})
    
    return render(request, "transit/transport.html", {})
