from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.messages import get_messages
from farm.tests import CommonTestSetupMixin, Order
from django.contrib.auth.models import Permission

from accounts.models import User
from .models import Quote, TransportBooking

class TestTransitAppViews(CommonTestSetupMixin, TestCase):
    def setUp(self):
        super().common_setup()
        checkout_url = reverse("farm:checkout")

        self.data = {
            "departure": "Nairobi",
            "delivery": "simbar",
            "weight": "400",
            "dimensions": "4x5x7",
            "name": "faru",
            "email": "faru@gmail.com",
            "phone": "+254723930893",
            "message": "this item is cool",

        }
        data = {
            "address": "msa",
            "payment_method": "card",
            "transport_option": "express",
            "pickup_location": "malindi",
        }

        self.client.post(checkout_url, data)
        self.order = Order.objects.get(pk=1)

        return data

    
    def test_transport_home_view(self):
        home_url = reverse("transit:transportquote")

        response = self.client.post(home_url, data=self.data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quote.objects.count(), 1)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn((f"Your quote request has been sent "
                       f"successfully. Thank you!"), messages)
    
    def test_all_transport_view(self):
        all_url = reverse("transit:transporthome")

        response = self.client.post(all_url)

        #self.assertEqual(response.status_code, 200)
        #self.assertEqual(TransportBooking.objects.count(), 1)
        #self.assertTemplateUsed(response, "transit/all_transport.html")















