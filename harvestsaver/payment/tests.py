from django.test import TestCase
from django.shortcuts import reverse
from django.utils import timezone

from farm.classmaxin import CommonTestSetupMixin
from farm.models import Product, Order, Cart, OrderItem
from transit.models import TransportBooking
from .models import Payment, Account


class TestPaymentViews(CommonTestSetupMixin, TestCase):
    def setUp(self):
        super().common_setup()
        checkout_url = reverse("farm:checkout")

        data = {
            "address": "msa",
            "payment_method": "pay_on_delivery",
            "transport_option": "express",
            "delivery_destination": 1,
            "upgrade_non_perishable_express": True,
        }

        # we need to create order and hub for test cases

        self.client.post(checkout_url, data)
        self.order = Order.objects.first()
        self.account = self.owner.account.account_balance
