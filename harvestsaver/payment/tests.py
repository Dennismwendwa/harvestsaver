from django.test import TestCase
from django.shortcuts import reverse
from django.utils import timezone

from farm.tests import CommonTestSetupMixin
from farm.models import Product, Order, Cart, OrderItem
from transit.models import TransportBooking
from .models import Payment, Account


class TestPaymentViews(CommonTestSetupMixin, TestCase):
    def setUp(self):
        super().common_setup()
        checkout_url = reverse("farm:checkout")

        data = {
            "address": "msa",
            "payment_method": "card",
            "transport_option": "express",
            "pickup_location": "malindi",
        }

        self.client.post(checkout_url, data)
        self.order = Order.objects.get(pk=1)
        self.account = self.owner.account.account_balance

    def test_payment_by_farmpay_service_view(self):
        payment_url = reverse("payment:checkout_payment", args=(self.order.pk,))
         
        
        response = self.client.post(payment_url)
        order = Order.objects.get(pk=1)
        account = Account.objects.get(user=self.owner)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cart.objects.count(), 0)
        self.assertEqual(order.status, "payed")
        self.assertEqual(account.total_payment, order.total_amount)
        self.assertTrue(account.last_transaction_date < timezone.now())
