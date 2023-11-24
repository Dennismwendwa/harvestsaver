from django.shortcuts import render
from .models import TransportBooking

def transporthome(request):
    return render(request, "transit/transport.html", {})
