from django.urls import reverse_lazy
from django.db.models import F, Q, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from utils.decorators import is_staff
from farm.models import Hub, Farm
from farm.forms import FarmForm, HubForm

@login_required
@is_staff
def admin_staff(request):
    """This is admin iew only for dashboard"""
    farms = Farm.objects.select_related("hub", "owner")
    hubs = Hub.objects.all()

    hubs_data = list(
        hubs.values("id", "name", "latitude", "longitude")
    )

    if request.method == "POST":
        print(request.POST)

        hub_form = HubForm(request.POST)
        if hub_form.is_valid():
            hub_form.save()
            messages.success(request, "New hub created successfully")
            return redirect("farm:admin_dashboard")
        else:
            hub_form = hub_form()

    form = FarmForm()
    hub_form = HubForm()

    context = {
        "farms": farms,
        "hubs": hubs,
        "form": form,
        "hub_form": hub_form,
        "hubs_data": hubs_data,
    }
    return render(request, "farm/admin/dashboard.html", context)

