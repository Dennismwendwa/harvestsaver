from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .forms import TransferRecordForm
from farm.models import Hub



def delivery_dashboard(request):
    
    if request.method == "POST":
        pass

    transferForm = TransferRecordForm()

    context={
        "transferForm": transferForm,
    }
    return render(request, "logistics/delivery/delivery_dashboard.html", context)

