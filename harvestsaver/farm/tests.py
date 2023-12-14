from django.test import TestCase
from django.shortcuts import reverse
from django.core.paginator import Page
from django.db.models.query import QuerySet
from django.core import mail

from .classmaxin import *
from .models import Product, Equipment, Category
from .models import EquipmentInquiry, Cart, Order, OrderItem
from transit.models import TransportBooking


        

class TestAllProductsListingview(ProductsTestSetupMixin, TestCase):
    def setUp(self):
        super().common_setup()
        

    def test_getting_all_product_view(self):
        response = self.client.get(self.all_products_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'farm/all_products.html')
        self.assertIn("page_object", response.context)
        self.assertIsInstance(response.context["page_object"], Page)
        self.assertEqual(len(response.context["page_object"].object_list), 4)
        self.assertEqual(response.context["page_object"].paginator.count, 10)

    def test_product_detail_view(self):
        product = Product.objects.get(pk=2)
        detail_url = reverse("farm:product_details",
                             args=[product.slug, product.pk])
        
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "farm/product_detail.html")
        self.assertContains(response, product.name)
        self.assertIn("product", response.context)
        self.assertContains(response, '<div class="product_details">')

    def test_product_detail_view_with_not_found(self):
        non_product_pk = 99
        detail_url = reverse("farm:product_details",
                              args=("non_produt", non_product_pk))

        with self.assertRaises(Product.DoesNotExist):
            response = self.client.get(detail_url)

            self.assertEqual(response.status_code, 404)

    def test_product_category_view(self):
        cat = Category.objects.get(name="fruits")
        cat_url = reverse("farm:products_category", args=(cat.slug,))
        response = self.client.get(cat_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "farm/category.html")
        self.assertContains(response, cat.name)
        self.assertIn("cat_products", response.context)
        self.assertIsInstance(response.context["cat_products"], QuerySet)
        self.assertGreater(len(response.context["cat_products"]), 0)

    def test_search_product_view(self):
        search_url = reverse("farm:search")

        data = {"query": "good"}

        response = self.client.post(search_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.context)
        self.assertContains(response, "good")
        self.assertTemplateUsed(response, "farm/search.html")

class TestEquipmentviews(EquipmentTestSetupMixin, TestCase):
    def setUp(self):
        super().common_setup()

            
    def test_all_equipments_view(self):
        response = self.client.get(self.all_equipments_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "farm/all_equipments.html")
        self.assertIn("page_object", response.context)
        self.assertIsInstance(response.context["page_object"], Page)
        self.assertEqual(len(response.context["page_object"].object_list), 4)
        self.assertEqual(response.context["page_object"].paginator.count, 10)


    def test_equipment_details_view(self):
        equipment = Equipment.objects.get(pk=3)
        details_url = reverse("farm:equipment_detail", args=(equipment.slug,))
        
        response = self.client.get(details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "farm/equipment_detail.html")
        self.assertContains(response, equipment.name)
        self.assertIn("equipment", response.context)

    def test_equipment_details_view_with_post_data(self):
        equipment = Equipment.objects.get(pk=3)
        details_url = reverse("farm:equipment_detail", args=(equipment.slug,))
        
        data = {
            "name": "django",
            "email": "django@gmail.com",
            "subject": "new equipment",
            "message": "tractor",
        }
        response = self.client.post(details_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(EquipmentInquiry.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Name: django", mail.outbox[0].body)

    def test_equipment_category_view(self):
        category_url = reverse("farm:equipment_category", args=(self.cat.slug,))

        equipments = Equipment.objects.filter(category=self.cat)
        
        response = self.client.get(category_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "farm/category.html")
        self.assertIn("category", response.context)
        self.assertContains(response, self.cat.name)
        self.assertGreater(len(response.context["equipments"]), 0)



class CheckoutViewTest(CommonTestSetupMixin, TestCase):
    def setUp(self):
        super().common_setup()

    def test_checkout_view(self):
        checkout_url = reverse("farm:checkout")
         
        response = self.client.get(checkout_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "farm/chackout.html")
        self.assertEqual(Cart.objects.count(), 4)
        self.assertIn("total", response.context)
        self.assertIn("shipping", response.context)
        self.assertIn("total_cost", response.context)
        self.assertEqual(response.context["total"], 1600)
        self.assertEqual(response.context["shipping"], 48)
        self.assertEqual(response.context["total_cost"], 1648)
        

    def test_checkout_view_with_post(self):
        data = {
            "address": "msa",
            "payment_method": "card",
            "transport_option": "express",
            "pickup_location": "malindi",
        }
        checkout_url = reverse("farm:checkout")

        response = self.client.post(checkout_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 4)
        self.assertEqual(TransportBooking.objects.count(), 1)
