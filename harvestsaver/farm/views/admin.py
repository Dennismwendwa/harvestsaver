from django.urls import reverse_lazy
from django.db.models import F, Q, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

def admin_staff(request):
    return render(request, "farm/admin/dashboard.html")

