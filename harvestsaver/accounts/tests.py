from django.test import TestCase, Client
from django.contrib.auth.models import Group, Permission
from django.contrib import messages
from django.shortcuts import reverse

from .models import User, Profile, FarmerProfile, BuyerProfile
from .models import EquipmentOwnerProfile, Contact
from payment.models import Account

class RegisterViewTest(TestCase):
    def setUp(self):
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
        self.second_user = {
            "first_name": "mwendwa", "last_name": "coll",
            "username": "mwendwa", "email": "mwendwa@gmail.com",
            "password1": "dennis12345", "password2": "dennis12345",
            "role": "equipment owner", "phone_number": "12345678",
            "gender": "male", "country": "kenya",
        }

    def test_register_view_with_valid_data(self):
        response = self.client.post(self.register_url, self.valid_data)
        user = User.objects.get(username="dennismwendwa")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="dennismwendwa").exists())
        self.assertTrue(Group.objects.filter(name="Farmer").exists())
        self.assertTrue(user.groups.filter(name="Farmer").exists())
        self.assertTrue(Account.objects.filter(user=user).exists())
        self.assertTrue(FarmerProfile.objects.filter(user=user).exists()) 
        self.assertTrue(user.has_perm("farm.view_product"))

    
    def test_register_view_with_existing_username(self):
        self.client.post(self.register_url, self.second_user)
        data = self.valid_data.copy()
        data["username"] = "mwendwa"
        response = self.client.post(self.register_url, data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        
        redirected_response = self.client.get(response.url)
        self.assertEqual(redirected_response.status_code, 200)
        self.assertContains(redirected_response, "username taken")

    
    def test_register_view_with_existing_email(self):
        user2 = self.second_user.copy()
        user2["username"] = "coll"
        user2["email"] = "dennis@gamil.com"
        self.client.post(self.register_url, user2)
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

        redirect_response = self.client.get(response.url)
        self.assertEqual(redirect_response.status_code, 200)
        self.assertContains(redirect_response, "email already in use")


    def test_register_view_with_short_password(self):
        user2 = self.second_user.copy()
        user2["username"] = "coll"
        user2["password1"] = "123456"
        user2["password2"] = "123456"
        response = self.client.post(self.register_url, user2)
        
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

        redirect_response = self.client.get(response.url)
        self.assertEqual(redirect_response.status_code, 200)
        self.assertContains(redirect_response, (f"Passward must have "
                                               f"8 or more characters"))

    def test_register_view_with_not_matching_password(self):
        user2 = self.second_user.copy()
        user2["password1"] = "dennis1234567"
        user2["password2"] = "dennis4567890"
        response = self.client.post(self.register_url, user2)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 302)

        redirect_response = self.client.get(response.url)
        self.assertEqual(redirect_response.status_code, 200)
        self.assertContains(redirect_response, "Password not matching")

    
    def test_register_view_group_creation(self):
        user3 = self.second_user.copy()
        user3["role"] = "customer"
        user3["username"] = "charo"
        user3["email"] = "charo@gmail.com"
        response1 = self.client.post(self.register_url, user3)
        response2 = self.client.post(self.register_url, self.valid_data)
        response3 = self.client.post(self.register_url, self.second_user)
       
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response3.status_code, 302)
        self.assertTrue(User.objects.filter(username="charo", is_customer=True).exists())

        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Group.objects.count(), 2)

