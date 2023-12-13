from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import reverse
from django.core import mail
from django.contrib.messages import get_messages

from .models import User, Profile, FarmerProfile, BuyerProfile
from .models import EquipmentOwnerProfile, Contact
from payment.models import Account
from farm.models import Product, Equipment


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
        self.client.post(self.register_url, self.second_user)
        response = self.client.post(self.register_url, self.valid_data)
        user = User.objects.get(username="dennismwendwa")
        user2 = User.objects.get(username="mwendwa")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="dennismwendwa").exists())
        self.assertTrue(Group.objects.filter(name="Farmer").exists())
        self.assertTrue(user.groups.filter(name="Farmer").exists())
        self.assertTrue(Account.objects.filter(user=user).exists())
        self.assertTrue(FarmerProfile.objects.filter(user=user).exists()) 
        self.assertTrue(user.has_perm("farm.view_product"))

        self.assertTrue(Group.objects.filter(name="Equipment owner").exists())
        self.assertTrue(EquipmentOwnerProfile.objects.filter(user=user2).exists())
        self.assertTrue(user2.has_perm("farm.view_equipment"))

    
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
        self.assertTrue(User.objects.filter(username="charo",
                                            is_customer=True).exists())
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Group.objects.count(), 2)
        
        model = "product"
        model2 = "equipment"
        group1 = Group.objects.get(name="Farmer")
        group2 = Group.objects.get(name="Equipment owner")
        content_type1 = ContentType.objects.get_for_model(Product)
        content_type2 = ContentType.objects.get_for_model(Equipment)

        view_permission = Permission.objects.get(codename=f"view_{model}",
                                                 content_type=content_type1)
        view_permission2 = Permission.objects.get(codename=f"view_{model2}",
                                                  content_type=content_type2)
        self.assertTrue(group1.permissions.filter(pk=view_permission.pk).exists())
        self.assertTrue(group2.permissions.filter(pk=view_permission2.pk).exists())


class LoginViewTest(TestCase):
    def setUp(self):
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.valid_user = {
            "first_name": "Fatuma",
            "last_name": "Omar",
            "username": "fatumaomar",
            "email": "fatuma@gamil.com",
            "password1": "fatuma12345",
            "password2": "fatuma12345",
            "role": "farmer",
            "phone_number": "08445563",
            "country": "Uganda",
            "gender": "female",
        }
   
    def test_login_view_with_valid_user(self):
        login_user = {"username": "fatumaomar", "password": "fatuma12345"}

        response = self.client.post(self.register_url, self.valid_user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(self.login_url, login_user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, expected_url=reverse("farm:farmer_dashboard"))

        user = User.objects.get(username="fatumaomar")
        self.assertTrue(user.is_authenticated)

    def test_login_view_with_wrong_password(self):
        user = {"username": "fatumaomar", "password": "12345"}
        self.client.post(self.register_url, self.valid_user)
        response = self.client.post(self.login_url, user, follow=True)
        
        self.assertContains(response, "Wrong password or username")
        self.assertEqual(User.objects.count(), 1)

    def test_login_view_with_wrong_username(self):
        user = {"username": "fatuma", "password": "fatuma12345"}
        self.client.post(self.register_url, self.valid_user)
        response = self.client.post(self.login_url, user, follow=True)

        self.assertContains(response, "Wrong password or username")
        self.assertEqual(User.objects.count(), 1)

    def test_login_view_redirects_after_successfull_login(self):
        login_user1 = {"username": "keva", "password": "fatuma12345"}
        login_user2 = {"username": "customer", "password": "fatuma12345"}
        login_user3 = {"username": "equipment", "password": "fatuma12345"}

        user1 = self.valid_user.copy()
        user1["username"] = "keva"
        user1["email"] = "keva@gmail.com"
        user1["role"] = "staff"
        self.client.post(self.register_url, user1)

        user2 = self.valid_user.copy()
        user2["username"] = "customer"
        user2["email"] = "customer@gmail.com"
        user2["role"] = "customer"
        self.client.post(self.register_url, user2)
        
        user3 = self.valid_user.copy()
        user3["username"] = "equipment"
        user3["email"] = "equipment@gmail.com"
        user3["role"] = "equipment owner"
        self.client.post(self.register_url, user3)

        response1 = self.client.post(self.login_url, login_user1)
        response2 = self.client.post(self.login_url, login_user2)
        response3 = self.client.post(self.login_url, login_user3)
        self.assertRedirects(response1, expected_url=reverse("farm:home"))
        self.assertRedirects(response2, expected_url=reverse("farm:home"))
        self.assertRedirects(response3, expected_url=reverse("farm:equipment_dashboard"))


class ContactViewTest(TestCase):
    def test_contact_view_with_valid_data(self):
        url = reverse("accounts:contact")
        data = {
            "name": "Dennis Mwendwa",
            "email": "dennis@gmail.com",
            "subject": "Testing cantact view",
            "message": "View success",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "New cantact form submission")
        self.assertIn("Name: Dennis Mwendwa", mail.outbox[0].body)
        self.assertIn("Email: dennis@gmail.com", mail.outbox[0].body)

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Your message has been sent. Thank you", messages)
    
    def test_contact_view_with_invalid_data(self):
        url = reverse("accounts:contact")
        data = {
            "name": "",
            "email": "not-email",
            "subject": "",
            "message": "",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
