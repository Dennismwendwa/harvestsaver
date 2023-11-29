from django.urls import path
from . import views

from .views import (
    CreateCheckoutSessionView,
    SuccessView,
    CancelView,
    stripe_webhook,
    StripeIntentView
)

app_name = "payment"

urlpatterns = [
    path("farm-payment/<int:pk>", views.create_checkoutfarmpayment, name="checkout_payment"),
    path("payment/<int:pk>", views.service_payment, name="servicepayment"),
    path('create-payment-intent/<pk>/', StripeIntentView.as_view(),
        name='create-payment-intent'),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('create-checkout-session/<int:pk>', CreateCheckoutSessionView.as_view(),
         name='create-checkout-session'),
]