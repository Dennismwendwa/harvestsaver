from rest_framework.test import APITestCase
from rest_framework import status
from django.shortcuts import reverse

from farm.models import Product
from farm.tests import ProductsTestSetupMixin
from .serializers import ProductSerializer


class ProductAPIViewTest(ProductsTestSetupMixin, APITestCase):
    def setUp(self):
        super().common_setup()
        
        self.products_url = reverse("api:products_api")

    def test_get_all_product(self):
        response = self.client.get(self.products_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
