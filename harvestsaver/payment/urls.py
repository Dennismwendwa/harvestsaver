from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("pay", views.create_checkoutfarmpayment, name="checkout_payment"),
]