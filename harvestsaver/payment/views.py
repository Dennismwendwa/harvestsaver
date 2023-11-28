from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction

from accounts.models import User
from .models import Account, Payment


def create_checkoutfarmpayment(request):
    
    if request.method == "POST":
        try:
            with transaction.atomic():
                pass

        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect("payment:payment_failed")