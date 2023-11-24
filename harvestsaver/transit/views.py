from django.shortcuts import render
from .models import TransportBooking, Quote

def transporthome(request):
    if request.method == "POST":
        pass
    
    return render(request, "transit/transport.html", {})
