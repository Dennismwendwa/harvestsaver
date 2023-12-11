from django.test import TestCase
from django.utils import timezone
from django.shortcuts import reverse
from django.core.paginator import Page
from django.core.files import File
import os

from accounts.models import User
from .models import Product, Equipment, Category


class TestAllProductsListingview(TestCase):
    def setUp(self):
        self.all_products_url = reverse("farm:all_products")
        self.register_url = reverse("accounts:register")

        self.valid_data = {
            "first_name": "Dennis",
            "last_name": "Mwendwa",
            "username": "dennismwendwa",
            "email": "dennis@gamil.com",
            "password1": "securepassword",
            "password2": "securepassword",
            "role": "farmer",
            "phone_number": "123456789",
            "gender": "male",
            "country": "kenya",
        }
        self.client.post(self.register_url, self.valid_data)
        owner = User.objects.get(username="dennismwendwa")
        cat = Category.objects.create(name="fruits", slug="fruits")
        
        file_path = os.path.join(os.path.dirname(
                                 os.path.dirname(
                                 os.path.abspath(__file__))),
                                 "media", "profile.png")
        for p in range(10):
            product = Product.objects.create(
                owner=owner, name=f"mango {p}", slug=f"mango {p}",
                category=cat, price=400,
                quantity=200, unit_of_measurement="kg", description="Very good",
                location="nairobi", harvest_date=timezone.now(),
            )
            product.image.save(f"sample_image{p}.jpg", 
                               File(open(file_path, "rb")))

    def test_getting_all_product_view(self):
        response = self.client.get(self.all_products_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'farm/all_products.html')
        self.assertIn("page_object", response.context)
        self.assertIsInstance(response.context['page_object'], Page)
        self.assertEqual(len(response.context['page_object'].object_list), 4)
        self.assertEqual(response.context['page_object'].paginator.count, 10)














