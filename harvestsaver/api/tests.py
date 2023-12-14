from rest_framework.test import APITestCase
from rest_framework import status
from django.shortcuts import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
import os

from accounts.models import User
from farm.models import Product, Category, Equipment, EquipmentCategory
from farm.classmaxin import ProductsTestSetupMixin, EquipmentTestSetupMixin
from .serializers import ProductSerializer


class ProductAPIViewTest(ProductsTestSetupMixin, APITestCase):
    def setUp(self):
        super().common_setup()
        
        self.owner = User.objects.get(username="dennismwendwa")
        self.cat = Category.objects.get(name="fruits")
        
        file_path = os.path.join(os.path.dirname(
                                 os.path.dirname(
                                 os.path.abspath(__file__))),
                                 "media", "profile.png")
        self.image_file = SimpleUploadedFile(name="image.jpg",
                                        content=open(file_path, "rb").read(),
                                        content_type="image/jpeg")

        self.product_data = {
                "owner": self.owner.pk, "name": "orange", "slug": "orange",
                "category": self.cat.pk, "price": 100,
                "quantity": 200, "unit_of_measurement":"kg",
                "description": "Very good", "location": "nairobi",
                "harvest_date": timezone.now().strftime('%Y-%m-%d'),
                "image": self.image_file,
        }

        self.new_data = {
                "owner": self.owner.pk, "name": "name updated", "slug": "name_updated",
                "category": self.cat.pk, "price": 600,
                "quantity": 500, "unit_of_measurement":"kg",
                "description": "The first product", "location": "kitui",
                "harvest_date": timezone.now().strftime('%Y-%m-%d'),
                "image": self.image_file,
        }

        self.products_url = reverse("api:products_api")

    def test_get_all_product(self):
        response = self.client.get(self.products_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(response.data[0]["name"], "mango 9")


    def test_create_product(self):

        response = self.client.post(self.products_url, self.product_data,
                                    format="multipart")
        product = Product.objects.get(pk=11)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 11)
        self.assertEqual(product.name, "orange")

    def test_invalid_product_data(self):
        data = {
            "owner": self.owner.pk, "name": "orange", "slug": "orange",
            "category": self.cat.pk, "price": 100,
            "quantity": 200, "unit_of_measurement":"kg",
        }

        response = self.client.post(self.products_url, data,
                                    format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)
        self.assertIn("description", response.data)
        self.assertIn("location", response.data)
        self.assertIn("harvest_date", response.data)
    
    def test_get_single_product_view(self):
        
        product = Product.objects.get(name="mango 9")

        detail_url = reverse("api:product_detail_api", args=(product.pk,))

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "mango 9")
        self.assertEqual(response.data["slug"], "mango-9")

    def test_update_single_product(self):

        product = Product.objects.get(name="mango 9")

        update_url = reverse("api:product_detail_api", args=(product.pk,))

        response = self.client.put(update_url, self.new_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "name updated")
        self.assertEqual(response.data["description"], "The first product")
        self.assertEqual(response.data["location"], "kitui")


    def test_search_products(self):
        query = "mango"

        search_url = reverse("api:product_search_api")

        response = self.client.get(search_url, {"query": query})
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data[0]["name"], "mango 9")
        self.assertEqual(data[1]["name"], "mango 8")

    def test_search_products_no_results(self):
        query = "no such product"

        search_url = reverse("api:product_search_api")

        response = self.client.get(search_url, {"query": query})
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 0)


class TestEquipmentAPIViews(EquipmentTestSetupMixin, APITestCase):
    def setUp(self):
        super().common_setup()

        self.cat = EquipmentCategory.objects.get(name="tractor")
        self.owner = User.objects.get(username="dennismwendwa")

        file_path = os.path.join(os.path.dirname(
                                 os.path.dirname(
                                 os.path.abspath(__file__))),
                                 "media", "profile.png")
        self.image_file = SimpleUploadedFile(name="image.jpg",
                                        content=open(file_path, "rb").read(),
                                        content_type="image/jpeg")
        
        self.new_data = {
                "name": "JCB", "slug": "JCB",
                "description": "good", "category": self.cat.pk,
                "owner": self.owner.pk, "location": "wote",
                "price_per_hour": 600, "image": self.image_file,
        }

        
    def test_get_all_equipents(self):
        equipments_url = reverse("api:equipments_api")

        response = self.client.get(equipments_url)

        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        self.assertEqual(response.data[9]["name"], "harvester_tractor 0")
        

    def test_get_single_equipment(self):
        equipment = Equipment.objects.get(name="harvester_tractor 9")
        equipment_url = reverse("api:equipment_deatil_api",
                                args=(equipment.pk,))

        response = self.client.get(equipment_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "harvester_tractor 9")

    def test_delete_equipment(self):
        equipment = Equipment.objects.get(name="harvester_tractor 9")
        equipment_url = reverse("api:equipment_deatil_api",
                                args=(equipment.pk,))

        response = self.client.delete(equipment_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Equipment deleted successfully")
        with self.assertRaises(Equipment.DoesNotExist):
            Equipment.objects.get(pk=equipment.pk)

