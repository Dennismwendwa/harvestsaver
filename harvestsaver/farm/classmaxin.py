from django.utils import timezone
from django.shortcuts import reverse
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import os
import io

from accounts.models import User
from .models import Product, Equipment, Category, EquipmentCategory
from .models import Cart


class EquipmentTestSetupMixin:
    def common_setup(self):
        self.all_equipments_url = reverse("farm:all_equipments")
        self.cat = EquipmentCategory.objects.create(name="tractor", slug="tractor")
        
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
        self.owner = User.objects.get(username="dennismwendwa")
        
        file_path = os.path.join(os.path.dirname(
                                 os.path.dirname(
                                 os.path.abspath(__file__))),
                                 "media", "profile.png")
        for e in range(10):
            equipment = Equipment.objects.create(
                name=f"harvester_tractor {e}", slug=f"harvester_tractor {e}",
                description="very good tractor", category=self.cat,
                owner=self.owner, location="shimba hills", price_per_hour=4000,
            )
            equipment.image.save(f"sample_image{e}.jpg", File(open(file_path, "rb")))
            image_data = io.BytesIO()
            image = Image.new("RGB", (100, 100), "white")
            image.save(image_data, format="JPEG")
            image_data.seek(0)

            equipment.image.save(f"sample_image{e}.jpg",
                                 SimpleUploadedFile("sample_image.jpg", image_data.read()))


class ProductsTestSetupMixin:
    def common_setup(self):
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
                quantity=200, unit_of_measurement="kg",
                description="Very good",location="nairobi",
                harvest_date=timezone.now(),
            )
            image_data = io.BytesIO()
            image = Image.new("RGB", (100, 100), "white")
            image.save(image_data, format="JPEG")
            image_data.seek(0)
            product.image.save(f"sample_image{p}.jpg", 
                               SimpleUploadedFile("sample_image.jpg", image_data.read()))
        
            
class CommonTestSetupMixin:
    def common_setup(self):
        self.all_products_url = reverse("farm:all_products")
        self.register_url = reverse("accounts:register")

        self.user = {
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
        self.client.post(self.register_url, self.user)
        self.client.login(username="dennismwendwa", password="securepassword")
        self.owner = User.objects.get(username="dennismwendwa")

        cat = Category.objects.create(name="fruits", slug="fruits")
        
        file_path = os.path.join(os.path.dirname(
                                 os.path.dirname(
                                 os.path.abspath(__file__))),
                                 "media", "profile.png")
        for p in range(10):
            product = Product.objects.create(
                owner=self.owner, name=f"mango {p}", slug=f"mango {p}",
                category=cat, price=400,
                quantity=200, unit_of_measurement="kg",
                description="Very good",location="nairobi",
                harvest_date=timezone.now(),
            )
            product.image.save(f"sample_image{p}.jpg", 
                               File(open(file_path, "rb")))

        for c in range(4):
            print("C", c)
            Cart.objects.create(
                product=Product.objects.get(pk=c+1), 
                customer=self.owner, quantity=1
            )

        data = {
            "address": "msa",
            "payment_method": "card",
            "transport_option": "express",
            "pickup_location": "malindi",
        }